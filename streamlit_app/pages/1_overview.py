"""
streamlit_app/pages/1_overview.py
🏠 Platform Overview — live connection test + snapshot KPIs
"""

import streamlit as st
import pandas as pd
from utils.snowflake_connector import run_query, test_connection, GOLD_TABLES

st.set_page_config(page_title="Overview", page_icon="🏠", layout="wide")
st.title("🏠 Platform Overview")
st.markdown("Live connection status and a snapshot of your GOLD layer data.")

# ── Connection check ──────────────────────────────────────────────────────────
st.subheader("🔌 Snowflake Connection")
col_conn, col_info = st.columns([1, 2])

with col_conn:
    if test_connection():
        st.success("✅ Connected to Snowflake")
        st.markdown("**Account:** `tejxpcq-vw92165`")
        st.markdown("**Database:** `SAAS_REVENUE_DB`")
        st.markdown("**Schema:** `GOLD`")
    else:
        st.error("❌ Connection failed — check `.env` credentials")

with col_info:
    st.markdown("### GOLD Layer Tables")
    for t in GOLD_TABLES:
        count_df = run_query(
            f"SELECT COUNT(*) AS cnt FROM SAAS_REVENUE_DB.GOLD.{t.upper()}"
        )
        if not count_df.empty:
            cnt = int(count_df.iloc[0].get("CNT", 0))
            st.markdown(f"- `{t}` — **{cnt:,} rows**")
        else:
            st.markdown(f"- `{t}` — ⚠️ unavailable")

st.markdown("---")

# ── Snapshot KPIs ─────────────────────────────────────────────────────────────
st.subheader("📊 Snapshot KPIs")

@st.cache_data(ttl=120)
def load_snapshot():
    return run_query("""
        SELECT
            (SELECT MAX(mrr_amount)
             FROM SAAS_REVENUE_DB.GOLD.mrr_monthly)                         AS latest_mrr,
            (SELECT MAX(arr_amount)
             FROM SAAS_REVENUE_DB.GOLD.arr_summary)                         AS latest_arr,
            (SELECT COUNT(*)
             FROM SAAS_REVENUE_DB.GOLD.churn_analysis
             WHERE YEAR(churn_date) = YEAR(CURRENT_DATE))                   AS churned_ytd,
            (SELECT ROUND(AVG(predicted_ltv), 0)
             FROM SAAS_REVENUE_DB.GOLD.customer_ltv)                        AS avg_ltv,
            (SELECT SUM(net_new_mrr)
             FROM SAAS_REVENUE_DB.GOLD.revenue_waterfall
             WHERE YEAR(month_date) = YEAR(CURRENT_DATE))                   AS net_new_ytd
    """)

snapshot = load_snapshot()
if not snapshot.empty:
    row = snapshot.iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Latest MRR",   f"${row.get('LATEST_MRR', 0):,.0f}")
    c2.metric("Latest ARR",   f"${row.get('LATEST_ARR', 0):,.0f}")
    c3.metric("Churned YTD",  f"{int(row.get('CHURNED_YTD', 0)):,}")
    c4.metric("Avg LTV",      f"${row.get('AVG_LTV', 0):,.0f}")
    net = row.get("NET_NEW_YTD", 0)
    c5.metric("Net New MRR YTD", f"${net:,.0f}", delta=f"{'▲' if net > 0 else '▼'}")
else:
    st.warning("Could not load snapshot KPIs. Verify Snowflake connection.")

st.markdown("---")
st.markdown("""
### 🗺️ Navigation Guide
| Page | What you'll find |
|---|---|
| 💬 AI Revenue Analyst | Natural-language Q&A powered by LangChain + GPT-4o |
| 📈 MRR & ARR | Revenue trends, segment breakdown, ARR summary |
| 🔄 Churn Analysis | Monthly churn, reasons, segment risk |
| 💎 Customer LTV | LTV distribution, cohort analysis, top customers |
| 🌊 Revenue Waterfall | New / Expansion / Contraction / Churn MRR |
""")