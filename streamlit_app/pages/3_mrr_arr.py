import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.snowflake_connector import run_query

st.set_page_config(page_title="MRR & ARR", page_icon="📈", layout="wide")
st.title("📈 MRR & ARR Analytics")
st.markdown("Monthly and Annual Recurring Revenue from Snowflake GOLD layer.")

@st.cache_data(ttl=300)
def load_mrr_kpis():
    return run_query("""
        SELECT
            MAX(MRR)                              AS latest_mrr,
            SUM(MRR)                              AS total_mrr_ytd,
            COUNT(DISTINCT CUSTOMER_ID)           AS active_customers,
            ROUND(AVG(MRR), 2)                    AS avg_mrr_per_customer
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        WHERE YEAR(INVOICE_MONTH) = YEAR(CURRENT_DATE)
    """)

@st.cache_data(ttl=300)
def load_mrr_trend():
    return run_query("""
        SELECT
            INVOICE_MONTH           AS month_date,
            SUM(MRR)                AS total_mrr,
            COUNT(DISTINCT CUSTOMER_ID) AS customers
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY INVOICE_MONTH
        ORDER BY INVOICE_MONTH
    """)

@st.cache_data(ttl=300)
def load_arr_summary():
    return run_query("""
        SELECT *
        FROM SAAS_REVENUE_DB.GOLD.arr_summary
        LIMIT 20
    """)

@st.cache_data(ttl=300)
def load_mrr_by_segment():
    return run_query("""
        SELECT
            INVOICE_MONTH           AS month_date,
            SEGMENT                 AS customer_segment,
            SUM(MRR)                AS segment_mrr
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY INVOICE_MONTH, SEGMENT
        ORDER BY INVOICE_MONTH
    """)

with st.spinner("Loading MRR data…"):
    kpis      = load_mrr_kpis()
    mrr_trend = load_mrr_trend()
    arr_data  = load_arr_summary()
    seg_data  = load_mrr_by_segment()

if not kpis.empty:
    row = kpis.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest MRR",         f"${row.get('LATEST_MRR', 0):,.0f}")
    c2.metric("MRR YTD Total",      f"${row.get('TOTAL_MRR_YTD', 0):,.0f}")
    c3.metric("Active Customers",   f"{int(row.get('ACTIVE_CUSTOMERS', 0)):,}")
    c4.metric("Avg MRR / Customer", f"${row.get('AVG_MRR_PER_CUSTOMER', 0):,.2f}")

st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("MRR Trend")
    if not mrr_trend.empty:
        mrr_trend.columns = [c.lower() for c in mrr_trend.columns]
        fig = px.line(mrr_trend, x="month_date", y="total_mrr",
            title="Monthly Recurring Revenue Over Time",
            labels={"total_mrr": "MRR ($)", "month_date": "Month"},
            template="plotly_dark", line_shape="spline")
        fig.update_traces(line_color="#00D4FF", line_width=3)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No MRR trend data available.")

with col2:
    st.subheader("ARR Summary")
    if not arr_data.empty:
        arr_data.columns = [c.lower() for c in arr_data.columns]
        st.dataframe(arr_data.head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No ARR data available.")

st.subheader("MRR by Customer Segment")
if not seg_data.empty:
    seg_data.columns = [c.lower() for c in seg_data.columns]
    fig2 = px.area(seg_data, x="month_date", y="segment_mrr",
        color="customer_segment",
        title="MRR Split by Customer Segment",
        template="plotly_dark",
        labels={"segment_mrr": "MRR ($)", "month_date": "Month"})
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No segment data available.")

with st.expander("🔍 View raw MRR data"):
    if not mrr_trend.empty:
        st.dataframe(mrr_trend, use_container_width=True)