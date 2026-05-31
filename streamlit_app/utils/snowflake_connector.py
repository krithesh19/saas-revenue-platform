"""
streamlit_app/utils/snowflake_connector.py
Centralised Snowflake connection — uses st.cache_resource so the
connection is reused across reruns and pages.
"""

import os
import pandas as pd
import streamlit as st
from snowflake.connector import connect, DictCursor
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_CFG = {
    "account":   os.getenv("SNOWFLAKE_ACCOUNT",   "tejxpcq-vw92165"),
    "user":      os.getenv("SNOWFLAKE_USER",       ""),
    "password":  os.getenv("SNOWFLAKE_PASSWORD",   ""),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE",  "SAAS_WH"),
    "database":  os.getenv("SNOWFLAKE_DATABASE",   "SAAS_REVENUE_DB"),
    "schema":    os.getenv("SNOWFLAKE_SCHEMA",     "GOLD"),
    "role":      os.getenv("SNOWFLAKE_ROLE",       "ACCOUNTADMIN"),
}

GOLD_TABLES = [
    "mrr_monthly",
    "arr_summary",
    "churn_analysis",
    "customer_ltv",
    "revenue_waterfall",
]


@st.cache_resource(show_spinner="Connecting to Snowflake…")
def get_connection():
    """Return a cached Snowflake connection."""
    try:
        conn = connect(**SNOWFLAKE_CFG)
        return conn
    except Exception as e:
        st.error(f"❌ Snowflake connection failed: {e}")
        return None


def run_query(sql: str, params: tuple = None) -> pd.DataFrame:
    """Execute SQL and return a DataFrame. Reconnects on stale cursor."""
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()


def get_table_schema(table: str) -> str:
    """Return CREATE TABLE DDL as a string (used by the LangChain agent)."""
    df = run_query(f"SHOW COLUMNS IN TABLE SAAS_REVENUE_DB.GOLD.{table.upper()}")
    if df.empty:
        return f"-- schema unavailable for {table}"
    lines = [f"-- {table}"]
    for _, row in df.iterrows():
        col = row.get("column_name", row.get("name", "unknown"))
        dtype = row.get("data_type", "VARCHAR")
        lines.append(f"  {col}  {dtype},")
    return "\n".join(lines)


def get_all_schemas() -> str:
    """Concatenate schemas for all 5 Gold tables (injected into LLM prompt)."""
    parts = []
    for t in GOLD_TABLES:
        parts.append(get_table_schema(t))
    return "\n\n".join(parts)


def test_connection() -> bool:
    conn = get_connection()
    if conn is None:
        return False
    try:
        df = run_query("SELECT CURRENT_VERSION()")
        return not df.empty
    except Exception:
        return False