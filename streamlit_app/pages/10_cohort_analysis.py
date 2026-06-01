"""
streamlit_app/pages/10_cohort_analysis.py
🔄 Cohort Analysis — Revenue retention by acquisition cohort
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.snowflake_connector import run_query
import io

st.set_page_config(page_title="Cohort Analysis", page_icon="🔄", layout="wide")
st.title("🔄 Cohort Analysis")
st.markdown("Track revenue retention by acquisition cohort — see which customers stay longest.")

@st.cache_data(ttl=300)
def load_cohort_data():
    return run_query("""
        SELECT
            acquisition_cohort,
            customer_segment,
            COUNT(*)                        AS customers,
            ROUND(AVG(predicted_ltv), 0)    AS avg_ltv,
            ROUND(SUM(predicted_ltv), 0)    AS total_ltv
        FROM SAAS_REVENUE_DB.GOLD.customer_ltv
        GROUP BY acquisition_cohort, customer_segment
        ORDER BY acquisition_cohort
    """)

@st.cache_data(ttl=300)
def load_mrr_cohort():
    return run_query("""
        SELECT
            DATE_TRUNC('month', month_date)  AS cohort_month,
            customer_segment,
            SUM(mrr_amount)                  AS total_mrr,
            COUNT(DISTINCT customer_id)      AS customers
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY 1, 2
        ORDER BY 1
    """)

with st.spinner("Loading cohort data..."):
    cohort_df = load_cohort_data()
    mrr_df    = load_mrr_cohort()

if cohort_df.empty:
    st.error("No cohort data found.")
    st.stop()

cohort_df.columns = [c.lower() for c in cohort_df.columns]
mrr_df.columns    = [c.lower() for c in mrr_df.columns]

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_cohorts   = cohort_df["acquisition_cohort"].nunique()
total_customers = cohort_df["customers"].sum()
avg_ltv         = cohort_df["avg_ltv"].mean()
best_cohort     = cohort_df.groupby("acquisition_cohort")["avg_ltv"].mean().idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Cohorts",    total_cohorts)
c2.metric("Total Customers",  f"{total_customers:,}")
c3.metric("Avg LTV",          f"${avg_ltv:,.0f}")
c4.metric("Best Cohort",      str(best_cohort))

st.markdown("---")

# ── LTV by cohort line chart ──────────────────────────────────────────────────
st.subheader("Average LTV by Acquisition Cohort")
cohort_summary = cohort_df.groupby("acquisition_cohort").agg(
    avg_ltv=("avg_ltv", "mean"),
    customers=("customers", "sum")
).reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=cohort_summary["acquisition_cohort"],
    y=cohort_summary["avg_ltv"],
    mode="lines+markers",
    name="Avg LTV",
    line=dict(color="#00D4FF", width=3),
    marker=dict(size=8),
))
fig.update_layout(
    template="plotly_dark", height=350,
    xaxis_title="Acquisition Cohort",
    yaxis_title="Average LTV ($)",
    title="LTV Trend by Acquisition Cohort",
)
st.plotly_chart(fig, use_container_width=True)

# ── Cohort heatmap ────────────────────────────────────────────────────────────
st.subheader("🗓️ Cohort Heatmap — LTV by Cohort and Segment")
pivot = cohort_df.pivot_table(
    index="acquisition_cohort",
    columns="customer_segment",
    values="avg_ltv",
    aggfunc="mean"
).fillna(0)

fig2 = px.imshow(
    pivot,
    title="Average LTV Heatmap by Cohort and Segment",
    template="plotly_dark",
    color_continuous_scale="Blues",
    labels=dict(x="Segment", y="Cohort", color="Avg LTV ($)"),
    aspect="auto",
)
fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)

# ── Customers per cohort ──────────────────────────────────────────────────────
st.subheader("👥 Customers per Cohort")
col1, col2 = st.columns(2)

with col1:
    fig3 = px.bar(
        cohort_summary,
        x="acquisition_cohort",
        y="customers",
        title="New Customers by Acquisition Cohort",
        template="plotly_dark",
        color="customers",
        color_continuous_scale="Blues",
        text_auto=True,
    )
    fig3.update_layout(height=320)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("📋 Cohort Summary Table")
    display = cohort_summary.copy()
    display["avg_ltv"]   = display["avg_ltv"].apply(lambda x: f"${x:,.0f}")
    display.columns      = ["Cohort", "Avg LTV", "Customers"]
    st.dataframe(display, use_container_width=True, hide_index=True)

# ── MRR by cohort month ───────────────────────────────────────────────────────
if not mrr_df.empty:
    st.subheader("📈 MRR by Cohort Month and Segment")
    mrr_df["cohort_month"] = pd.to_datetime(mrr_df["cohort_month"])
    fig4 = px.area(
        mrr_df,
        x="cohort_month",
        y="total_mrr",
        color="customer_segment",
        title="MRR Contribution by Segment Over Time",
        template="plotly_dark",
        labels={"total_mrr": "MRR ($)", "cohort_month": "Month"},
    )
    fig4.update_layout(height=350)
    st.plotly_chart(fig4, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💡 Cohort Insights")
best_ltv  = cohort_summary.loc[cohort_summary["avg_ltv"].idxmax()]
worst_ltv = cohort_summary.loc[cohort_summary["avg_ltv"].idxmin()]
st.success(f"**Best cohort:** {best_ltv['acquisition_cohort']} with avg LTV of ${best_ltv['avg_ltv']:,.0f}")
st.error(f"**Weakest cohort:** {worst_ltv['acquisition_cohort']} with avg LTV of ${worst_ltv['avg_ltv']:,.0f}")

# ── Excel export ──────────────────────────────────────────────────────────────
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    cohort_df.to_excel(writer, index=False, sheet_name="Cohort Analysis")
st.download_button(
    label="📥 Download as Excel",
    data=buffer.getvalue(),
    file_name="cohort_analysis.xlsx",
    mime="application/vnd.ms-excel",
)