import streamlit as st
import pandas as pd
import plotly.express as px
from utils.snowflake_connector import run_query

st.set_page_config(page_title="Customer LTV", page_icon="💎", layout="wide")
st.title("💎 Customer Lifetime Value")
st.markdown("Understand the long-term revenue value of your customer base.")

@st.cache_data(ttl=300)
def load_ltv_summary():
    return run_query("""
        SELECT
            COUNT(*)                          AS total_customers,
            ROUND(AVG(PROJECTED_LTV), 0)      AS avg_ltv,
            ROUND(MAX(PROJECTED_LTV), 0)      AS max_ltv,
            ROUND(SUM(PROJECTED_LTV), 0)      AS total_predicted_ltv
        FROM SAAS_REVENUE_DB.GOLD.customer_ltv
    """)

@st.cache_data(ttl=300)
def load_ltv_distribution():
    return run_query("""
        SELECT
            PROJECTED_LTV       AS predicted_ltv,
            SEGMENT             AS customer_segment,
            SIGNUP_DATE         AS acquisition_cohort
        FROM SAAS_REVENUE_DB.GOLD.customer_ltv
        ORDER BY PROJECTED_LTV DESC
        LIMIT 500
    """)

@st.cache_data(ttl=300)
def load_ltv_by_segment():
    return run_query("""
        SELECT
            SEGMENT                           AS customer_segment,
            ROUND(AVG(PROJECTED_LTV), 0)      AS avg_ltv,
            ROUND(MAX(PROJECTED_LTV), 0)      AS max_ltv,
            COUNT(*)                          AS customers
        FROM SAAS_REVENUE_DB.GOLD.customer_ltv
        GROUP BY SEGMENT
        ORDER BY avg_ltv DESC
    """)

@st.cache_data(ttl=300)
def load_ltv_by_cohort():
    return run_query("""
        SELECT
            DATE_TRUNC('month', SIGNUP_DATE)  AS acquisition_cohort,
            ROUND(AVG(PROJECTED_LTV), 0)      AS avg_ltv,
            COUNT(*)                          AS customers
        FROM SAAS_REVENUE_DB.GOLD.customer_ltv
        GROUP BY 1
        ORDER BY 1
    """)

@st.cache_data(ttl=300)
def load_top_customers():
    return run_query("""
        SELECT
            CUSTOMER_ID,
            COMPANY_NAME,
            SEGMENT             AS customer_segment,
            SIGNUP_DATE         AS acquisition_cohort,
            ROUND(PROJECTED_LTV, 0) AS predicted_ltv
        FROM SAAS_REVENUE_DB.GOLD.customer_ltv
        ORDER BY PROJECTED_LTV DESC
        LIMIT 20
    """)

with st.spinner("Loading LTV data…"):
    summary   = load_ltv_summary()
    dist_data = load_ltv_distribution()
    by_seg    = load_ltv_by_segment()
    by_cohort = load_ltv_by_cohort()
    top_cust  = load_top_customers()

if not summary.empty:
    row = summary.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers",     f"{int(row.get('TOTAL_CUSTOMERS', 0)):,}")
    c2.metric("Avg Predicted LTV",   f"${row.get('AVG_LTV', 0):,.0f}")
    c3.metric("Max LTV",             f"${row.get('MAX_LTV', 0):,.0f}")
    c4.metric("Total Predicted LTV", f"${row.get('TOTAL_PREDICTED_LTV', 0):,.0f}")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("LTV Distribution")
    if not dist_data.empty:
        dist_data.columns = [c.lower() for c in dist_data.columns]
        fig = px.histogram(dist_data, x="predicted_ltv", color="customer_segment",
            nbins=40, title="LTV Distribution by Segment",
            template="plotly_dark",
            labels={"predicted_ltv": "Predicted LTV ($)"})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Avg LTV by Segment")
    if not by_seg.empty:
        by_seg.columns = [c.lower() for c in by_seg.columns]
        fig2 = px.bar(by_seg, x="customer_segment", y="avg_ltv",
            color="avg_ltv",
            title="Average LTV by Customer Segment",
            template="plotly_dark", text_auto=".2s",
            color_continuous_scale="Blues")
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

st.subheader("Avg LTV by Acquisition Cohort")
if not by_cohort.empty:
    by_cohort.columns = [c.lower() for c in by_cohort.columns]
    fig3 = px.line(by_cohort, x="acquisition_cohort", y="avg_ltv",
        title="Customer LTV by Acquisition Cohort",
        template="plotly_dark", markers=True,
        labels={"avg_ltv": "Avg LTV ($)", "acquisition_cohort": "Cohort"})
    fig3.update_traces(line_color="#00D4FF", line_width=2)
    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("🏆 Top 20 Customers by LTV")
if not top_cust.empty:
    top_cust.columns = [c.lower() for c in top_cust.columns]
    st.dataframe(
        top_cust.style.format({"predicted_ltv": "${:,.0f}"}),
        use_container_width=True, hide_index=True)