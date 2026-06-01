import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.snowflake_connector import run_query

st.set_page_config(page_title="Churn Analysis", page_icon="🔄", layout="wide")
st.title("🔄 Churn Analysis")
st.markdown("Understand where and why customers are leaving.")

@st.cache_data(ttl=300)
def load_churn_summary():
    return run_query("""
        SELECT
            COUNT(*)                  AS total_churned,
            SUM(LOST_MRR)             AS total_lost_mrr,
            ROUND(AVG(LOST_MRR), 2)   AS avg_lost_mrr,
            MIN(CHURN_MONTH)          AS first_churn,
            MAX(CHURN_MONTH)          AS latest_churn
        FROM SAAS_REVENUE_DB.GOLD.churn_analysis
    """)

@st.cache_data(ttl=300)
def load_churn_by_month():
    return run_query("""
        SELECT
            DATE_TRUNC('month', CHURN_MONTH) AS churn_month,
            COUNT(*)                          AS churned_customers,
            SUM(LOST_MRR)                     AS lost_mrr
        FROM SAAS_REVENUE_DB.GOLD.churn_analysis
        GROUP BY 1
        ORDER BY 1
    """)

@st.cache_data(ttl=300)
def load_churn_by_reason():
    return run_query("""
        SELECT
            CHURN_CATEGORY   AS churn_reason,
            COUNT(*)         AS count,
            SUM(LOST_MRR)    AS lost_mrr
        FROM SAAS_REVENUE_DB.GOLD.churn_analysis
        GROUP BY CHURN_CATEGORY
        ORDER BY lost_mrr DESC
    """)

@st.cache_data(ttl=300)
def load_churn_by_segment():
    return run_query("""
        SELECT
            SEGMENT              AS customer_segment,
            COUNT(*)             AS churned_customers,
            SUM(LOST_MRR)        AS lost_mrr,
            ROUND(AVG(LOST_MRR), 0) AS avg_lost_mrr
        FROM SAAS_REVENUE_DB.GOLD.churn_analysis
        GROUP BY SEGMENT
        ORDER BY lost_mrr DESC
    """)

with st.spinner("Loading churn data…"):
    summary    = load_churn_summary()
    by_month   = load_churn_by_month()
    by_reason  = load_churn_by_reason()
    by_segment = load_churn_by_segment()

if not summary.empty:
    row = summary.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Churned Customers", f"{int(row.get('TOTAL_CHURNED', 0)):,}")
    c2.metric("Total Lost MRR",          f"${row.get('TOTAL_LOST_MRR', 0):,.0f}")
    c3.metric("Avg Lost MRR / Customer", f"${row.get('AVG_LOST_MRR', 0):,.0f}")

st.markdown("---")

col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("Monthly Churn Trend")
    if not by_month.empty:
        by_month.columns = [c.lower() for c in by_month.columns]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=by_month["churn_month"], y=by_month["churned_customers"],
            name="Churned Customers", marker_color="#FF6B6B"))
        fig.add_trace(go.Scatter(
            x=by_month["churn_month"], y=by_month["lost_mrr"],
            name="Lost MRR ($)", yaxis="y2",
            line=dict(color="#FFD700", width=2), mode="lines+markers"))
        fig.update_layout(
            template="plotly_dark",
            yaxis2=dict(overlaying="y", side="right", title="Lost MRR ($)"),
            height=350, legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Churn by Reason")
    if not by_reason.empty:
        by_reason.columns = [c.lower() for c in by_reason.columns]
        fig2 = px.pie(by_reason, values="lost_mrr", names="churn_reason",
            title="Lost MRR by Churn Reason",
            template="plotly_dark", hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu)
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

st.subheader("Churn by Customer Segment")
if not by_segment.empty:
    by_segment.columns = [c.lower() for c in by_segment.columns]
    fig3 = px.bar(by_segment, x="customer_segment", y="lost_mrr",
        color="churned_customers",
        title="Lost MRR and Volume by Segment",
        template="plotly_dark", text_auto=".2s",
        color_continuous_scale="Reds")
    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No segment churn data available.")

with st.expander("🔍 Raw churn data"):
    full = run_query("SELECT * FROM SAAS_REVENUE_DB.GOLD.churn_analysis LIMIT 200")
    if not full.empty:
        st.dataframe(full, use_container_width=True, hide_index=True)