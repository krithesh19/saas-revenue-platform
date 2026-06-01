"""
SaaS Revenue Intelligence Platform — Nightly Pipeline DAG
=========================================================
Schedule  : 02:00 UTC every night
Pipeline  : ETL (extract → load to Snowflake RAW) →
            dbt run (transforms RAW → SILVER → GOLD) →
            dbt test (data quality checks) →
            Slack/email alert (success or failure)

Snowflake : account=tejxpcq-vw92165  db=SAAS_REVENUE_DB
            warehouse=SAAS_WH        schema=GOLD

Author    : Kritheshvar Vinothkumar
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.utils.trigger_rule import TriggerRule

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Default args
# ──────────────────────────────────────────────
DEFAULT_ARGS: dict[str, Any] = {
    "owner": "kritheshvar",
    "depends_on_past": False,
    "email": ["kritheshvar@youremail.com"],      # ← update
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
}

# ──────────────────────────────────────────────
# Airflow Variables  (set once via UI / CLI)
# ──────────────────────────────────────────────
# airflow variables set SNOWFLAKE_CONN_ID   "snowflake_saas"
# airflow variables set SLACK_WEBHOOK_URL   "https://hooks.slack.com/..."
# airflow variables set DBT_PROJECT_DIR     "/opt/airflow/dbt/saas_revenue"
# airflow variables set DBT_PROFILES_DIR    "/opt/airflow/dbt/profiles"
SNOWFLAKE_CONN_ID = Variable.get("SNOWFLAKE_CONN_ID", default_var="snowflake_saas")
SLACK_WEBHOOK_URL = Variable.get("SLACK_WEBHOOK_URL", default_var="")
DBT_PROJECT_DIR   = Variable.get("DBT_PROJECT_DIR",   default_var="/opt/airflow/dbt/saas_revenue")
DBT_PROFILES_DIR  = Variable.get("DBT_PROFILES_DIR",  default_var="/opt/airflow/dbt/profiles")

# ──────────────────────────────────────────────
# Snowflake connection settings
# ──────────────────────────────────────────────
SNOWFLAKE_CONFIG = {
    "account":   "tejxpcq-vw92165",
    "database":  "SAAS_REVENUE_DB",
    "warehouse": "SAAS_WH",
    "schema":    "GOLD",
}


# ══════════════════════════════════════════════
# Task functions
# ══════════════════════════════════════════════

def check_snowflake_connection(**context) -> None:
    """Verify Snowflake is reachable before starting the pipeline."""
    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_TIMESTAMP(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
    row = cursor.fetchone()
    logger.info(
        "Snowflake OK — ts=%s  wh=%s  db=%s",
        row[0], row[1], row[2],
    )
    cursor.close()
    conn.close()


def extract_saas_metrics(**context) -> dict:
    """
    Extract SaaS metrics from source systems.

    In production replace the stub below with real API calls:
      - Stripe  → MRR, churn, new subscriptions
      - HubSpot → pipeline, ARR by segment
      - Internal DB → product usage events

    Returns a dict pushed to XCom for the loader task.
    """
    execution_date = context["execution_date"]
    logger.info("Extracting metrics for %s", execution_date.date())

    # ── Stub: replace with actual API / DB calls ──────────────────────
    raw_metrics = {
        "execution_date": str(execution_date.date()),
        "mrr_data": [
            {"customer_id": "C001", "plan": "enterprise", "mrr": 4999.0},
            {"customer_id": "C002", "plan": "growth",     "mrr": 999.0},
            {"customer_id": "C003", "plan": "starter",    "mrr": 99.0},
        ],
        "churn_events": [],
        "new_subscriptions": [
            {"customer_id": "C004", "plan": "growth", "mrr": 999.0},
        ],
    }
    # ─────────────────────────────────────────────────────────────────

    record_count = (
        len(raw_metrics["mrr_data"])
        + len(raw_metrics["churn_events"])
        + len(raw_metrics["new_subscriptions"])
    )
    logger.info("Extracted %d records", record_count)

    # Push to XCom so load task can read it
    context["ti"].xcom_push(key="raw_metrics", value=raw_metrics)
    return raw_metrics


def load_to_snowflake_raw(**context) -> None:
    """
    Load extracted metrics into Snowflake RAW schema via a staging table.

    Uses a MERGE pattern so the nightly job is idempotent —
    re-running won't create duplicate rows.
    """
    ti = context["ti"]
    raw_metrics: dict = ti.xcom_pull(
        task_ids="extract_saas_metrics", key="raw_metrics"
    )
    execution_date = raw_metrics["execution_date"]

    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()

    try:
        # ── Ensure RAW tables exist ─────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SAAS_REVENUE_DB.RAW.RAW_MRR_EVENTS (
                EVENT_DATE   DATE,
                CUSTOMER_ID  VARCHAR(50),
                PLAN         VARCHAR(50),
                MRR          NUMBER(12,2),
                EVENT_TYPE   VARCHAR(30),
                LOADED_AT    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)

        # ── Deduplicate: delete today's existing rows ───────────────
        cursor.execute(
            "DELETE FROM SAAS_REVENUE_DB.RAW.RAW_MRR_EVENTS WHERE EVENT_DATE = %s",
            (execution_date,),
        )

        # ── Insert MRR snapshot ─────────────────────────────────────
        for row in raw_metrics["mrr_data"]:
            cursor.execute(
                """
                INSERT INTO SAAS_REVENUE_DB.RAW.RAW_MRR_EVENTS
                    (EVENT_DATE, CUSTOMER_ID, PLAN, MRR, EVENT_TYPE)
                VALUES (%s, %s, %s, %s, 'MRR_SNAPSHOT')
                """,
                (execution_date, row["customer_id"], row["plan"], row["mrr"]),
            )

        # ── Insert new subscriptions ────────────────────────────────
        for row in raw_metrics["new_subscriptions"]:
            cursor.execute(
                """
                INSERT INTO SAAS_REVENUE_DB.RAW.RAW_MRR_EVENTS
                    (EVENT_DATE, CUSTOMER_ID, PLAN, MRR, EVENT_TYPE)
                VALUES (%s, %s, %s, %s, 'NEW_SUBSCRIPTION')
                """,
                (execution_date, row["customer_id"], row["plan"], row["mrr"]),
            )

        conn.commit()
        logger.info(
            "Loaded %d MRR + %d new-sub rows for %s",
            len(raw_metrics["mrr_data"]),
            len(raw_metrics["new_subscriptions"]),
            execution_date,
        )

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def run_dbt_models(**context) -> None:
    """
    Execute dbt run to transform RAW → SILVER → GOLD.

    Runs:
      - staging models   (RAW → SILVER)
      - mart models      (SILVER → GOLD: mrr, churn, arr, ltv)
    """
    import subprocess

    dbt_cmd = [
        "dbt", "run",
        "--project-dir", DBT_PROJECT_DIR,
        "--profiles-dir", DBT_PROFILES_DIR,
        "--target", "prod",
        "--vars", json.dumps({"execution_date": str(context["execution_date"].date())}),
        "--full-refresh" if context.get("params", {}).get("full_refresh") else "--select", "tag:nightly",
    ]
    # Remove --full-refresh flag placeholder if not set
    dbt_cmd = [c for c in dbt_cmd if c != "--full-refresh"]

    logger.info("Running: %s", " ".join(dbt_cmd))
    result = subprocess.run(dbt_cmd, capture_output=True, text=True, check=False)

    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(f"dbt run failed:\n{result.stderr}")

    logger.info("dbt run completed successfully")


def run_dbt_tests(**context) -> None:
    """
    Execute dbt test to enforce data quality on GOLD models.

    Tests include:
      - not_null checks on primary keys and MRR columns
      - unique constraints on customer snapshots
      - accepted_values for plan types
      - revenue reconciliation (custom test)
    """
    import subprocess

    dbt_cmd = [
        "dbt", "test",
        "--project-dir", DBT_PROJECT_DIR,
        "--profiles-dir", DBT_PROFILES_DIR,
        "--target", "prod",
        "--select", "tag:nightly",
        "--store-failures",         # persist failing rows to Snowflake for debugging
    ]

    logger.info("Running: %s", " ".join(dbt_cmd))
    result = subprocess.run(dbt_cmd, capture_output=True, text=True, check=False)

    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(f"dbt test failed:\n{result.stderr}")

    # Push test summary to XCom for the success notification
    context["ti"].xcom_push(key="dbt_test_output", value=result.stdout[-2000:])
    logger.info("dbt tests passed")


def branch_on_pipeline_result(**context) -> str:
    """
    BranchPythonOperator: route to success or failure notification.
    (Airflow handles task state — this is only reached on success.)
    """
    return "send_success_alert"


def build_success_message(**context) -> str:
    execution_date = context["execution_date"].strftime("%Y-%m-%d")
    return (
        f":white_check_mark: *SaaS Revenue Pipeline — SUCCESS*\n"
        f"> *Date:* {execution_date}\n"
        f"> *Warehouse:* {SNOWFLAKE_CONFIG['warehouse']}\n"
        f"> *Database:* {SNOWFLAKE_CONFIG['database']}\n"
        f"> All dbt models ran and tests passed.\n"
        f"> Dashboard: https://krithesh-saas-platform.streamlit.app"
    )


def send_success_alert(**context) -> None:
    """Send a Slack success notification."""
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not set — skipping Slack alert")
        return

    message = build_success_message(**context)
    import urllib.request
    payload = json.dumps({"text": message}).encode()
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=10)
    logger.info("Success alert sent to Slack")


def send_failure_alert(**context) -> None:
    """Send a Slack failure alert with task context."""
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not set — skipping Slack alert")
        return

    execution_date = context["execution_date"].strftime("%Y-%m-%d")
    exception = context.get("exception", "Unknown error")
    failed_task = context.get("task_instance").task_id

    message = (
        f":red_circle: *SaaS Revenue Pipeline — FAILED*\n"
        f"> *Date:* {execution_date}\n"
        f"> *Failed task:* `{failed_task}`\n"
        f"> *Error:* {str(exception)[:300]}\n"
        f"> Check Airflow logs for details."
    )

    import urllib.request
    payload = json.dumps({"text": message}).encode()
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=10)
    logger.info("Failure alert sent to Slack")


# ══════════════════════════════════════════════
# DAG definition
# ══════════════════════════════════════════════

with DAG(
    dag_id="saas_revenue_nightly_pipeline",
    description="Nightly ETL → dbt → test → alert for SaaS Revenue Intelligence Platform",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 2 * * *",    # 02:00 UTC every night
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,                # prevent overlapping runs
    tags=["saas", "revenue", "snowflake", "dbt", "nightly"],
    params={
        "full_refresh": False,        # set to True via Airflow UI to force full dbt refresh
    },
    doc_md="""
## SaaS Revenue Intelligence — Nightly Pipeline

**Stack:** Snowflake · dbt · Apache Airflow · Streamlit

### Schedule
Runs at **02:00 UTC** every night (safe margin after midnight EST).

### Pipeline steps
| Step | Task | Description |
|------|------|-------------|
| 1 | `check_snowflake_conn` | Verify connectivity before starting |
| 2a | `extract_saas_metrics` | Pull MRR, churn, new subs from source |
| 2b | `load_to_snowflake_raw` | Idempotent load into RAW schema |
| 3 | `run_dbt_models` | Transform RAW → SILVER → GOLD |
| 4 | `run_dbt_tests` | Data quality checks on GOLD models |
| 5a | `send_success_alert` | Slack notification on success |
| 5b | `send_failure_alert` | Slack alert with error context on failure |

### Snowflake
- Account: `tejxpcq-vw92165`
- Database: `SAAS_REVENUE_DB`
- Warehouse: `SAAS_WH`
- Gold schema: `GOLD`
""",
) as dag:

    # ── Task 1: health check ─────────────────────────────────────────
    t_check_conn = PythonOperator(
        task_id="check_snowflake_conn",
        python_callable=check_snowflake_connection,
    )

    # ── Task 2a: extract ─────────────────────────────────────────────
    t_extract = PythonOperator(
        task_id="extract_saas_metrics",
        python_callable=extract_saas_metrics,
        execution_timeout=timedelta(minutes=20),
    )

    # ── Task 2b: load ────────────────────────────────────────────────
    t_load = PythonOperator(
        task_id="load_to_snowflake_raw",
        python_callable=load_to_snowflake_raw,
        execution_timeout=timedelta(minutes=10),
    )

    # ── Task 3: dbt run ──────────────────────────────────────────────
    t_dbt_run = PythonOperator(
        task_id="run_dbt_models",
        python_callable=run_dbt_models,
        execution_timeout=timedelta(minutes=30),
    )

    # ── Task 4: dbt test ─────────────────────────────────────────────
    t_dbt_test = PythonOperator(
        task_id="run_dbt_tests",
        python_callable=run_dbt_tests,
        execution_timeout=timedelta(minutes=20),
    )

    # ── Task 5a: success alert ───────────────────────────────────────
    t_success = PythonOperator(
        task_id="send_success_alert",
        python_callable=send_success_alert,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # ── Task 5b: failure alert (fires if ANY upstream task fails) ────
    t_failure = PythonOperator(
        task_id="send_failure_alert",
        python_callable=send_failure_alert,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    # ── Dependencies ─────────────────────────────────────────────────
    #
    #   check_snowflake_conn
    #         ├── extract_saas_metrics
    #         │         └── load_to_snowflake_raw
    #         │                   └── run_dbt_models
    #         │                             └── run_dbt_tests
    #         │                                       └── send_success_alert
    #         └─────────────────────────────────────────────────────────┘
    #                                                   send_failure_alert  ← fires on any failure

    t_check_conn >> [t_extract]
    t_extract >> t_load
    t_load >> t_dbt_run
    t_dbt_run >> t_dbt_test
    t_dbt_test >> t_success

    # failure alert wired to every critical task
    [t_extract, t_load, t_dbt_run, t_dbt_test] >> t_failure
