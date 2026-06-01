import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.snowflake_connector import run_query

st.set_page_config(page_title="Revenue Waterfall", page_icon="🌊", layout="wide")
st.title("🌊 Revenue Waterfall")
st.markdown("MRR movement analysis — see how revenue changes month over month.")

@st.cache_data(ttl=300)
def load_waterfall():
    return run_query("""
        SELECT
            INVOICE_MONTH,
            MRR_MOVEMENT_TYPE,
            CUSTOMER_COUNT,
            TOTAL_MRR,
            MRR_CHANGE
        FROM SAAS_REVENUE_DB.GOLD.revenue_waterfall
        ORDER BY INVOICE_MONTH
    """)

@st.cache_data(ttl=300)
def load_waterfall_totals():
    return run_query("""
        SELECT
            SUM(TOTAL_MRR)    AS total_mrr,
            SUM(MRR_CHANGE)   AS total_mrr_change,
            SUM(CUSTOMER_COUNT) AS total_customers
        FROM SAAS_REVENUE_DB.GOLD.revenue_waterfall
        WHERE YEAR(INVOICE_MONTH) = YEAR(CURRENT_DATE)
    """)

with st.spinner("Loading waterfall data…"):
    wf_data   = load_waterfall()
    wf_totals = load_waterfall_totals()

if not wf_totals.empty:
    row = wf_totals.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total MRR YTD",      f"${row.get('TOTAL_MRR', 0):,.0f}")
    c2.metric("Total MRR Change",   f"${row.get('TOTAL_MRR_CHANGE', 0):,.0f}")
    c3.metric("Total Customers",    f"{int(row.get('TOTAL_CUSTOMERS', 0)):,}")

st.markdown("---")

if not wf_data.empty:
    wf_data.columns = [c.lower() for c in wf_data.columns]

    st.subheader("MRR by Movement Type")
    fig = px.bar(
        wf_data,
        x="invoice_month",
        y="total_mrr",
        color="mrr_movement_type",
        title="MRR by Movement Type Over Time",
        template="plotly_dark",
        labels={"total_mrr": "MRR ($)", "invoice_month": "Month"},
        barmode="group",
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("MRR Change Over Time")
    fig2 = px.bar(
        wf_data,
        x="invoice_month",
        y="mrr_change",
        color="mrr_movement_type",
        title="MRR Change by Movement Type",
        template="plotly_dark",
        labels={"mrr_change": "MRR Change ($)", "invoice_month": "Month"},
    )
    fig2.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Customer Count by Movement Type")
    fig3 = px.line(
        wf_data,
        x="invoice_month",
        y="customer_count",
        color="mrr_movement_type",
        title="Customer Count by Movement Type",
        template="plotly_dark",
        markers=True,
        labels={"customer_count": "Customers", "invoice_month": "Month"},
    )
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("🔍 View raw waterfall data"):
        st.dataframe(wf_data, use_container_width=True, hide_index=True)
else:
    st.info("No waterfall data found.")