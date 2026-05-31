"""
streamlit_app/pages/6_waterfall.py
🌊 Revenue Waterfall Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.snowflake_connector import run_query

st.set_page_config(page_title="Revenue Waterfall", page_icon="🌊", layout="wide")
st.title("🌊 Revenue Waterfall")
st.markdown("New, Expansion, Contraction, and Churn MRR — the four levers of SaaS growth.")

@st.cache_data(ttl=300)
def load_waterfall():
    return run_query("""
        SELECT
            month_date,
            new_mrr,
            expansion_mrr,
            contraction_mrr,
            churn_mrr,
            net_new_mrr
        FROM SAAS_REVENUE_DB.GOLD.revenue_waterfall
        ORDER BY month_date
    """)

@st.cache_data(ttl=300)
def load_waterfall_totals():
    return run_query("""
        SELECT
            SUM(new_mrr)         AS total_new,
            SUM(expansion_mrr)   AS total_expansion,
            SUM(contraction_mrr) AS total_contraction,
            SUM(churn_mrr)       AS total_churn,
            SUM(net_new_mrr)     AS total_net_new
        FROM SAAS_REVENUE_DB.GOLD.revenue_waterfall
        WHERE YEAR(month_date) = YEAR(CURRENT_DATE)
    """)

with st.spinner("Loading waterfall data…"):
    wf_data   = load_waterfall()
    wf_totals = load_waterfall_totals()

if not wf_totals.empty:
    row = wf_totals.iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("New MRR YTD",     f"${row.get('TOTAL_NEW', 0):,.0f}")
    c2.metric("Expansion YTD",   f"${row.get('TOTAL_EXPANSION', 0):,.0f}")
    c3.metric("Contraction YTD", f"${row.get('TOTAL_CONTRACTION', 0):,.0f}")
    c4.metric("Churn MRR YTD",   f"${row.get('TOTAL_CHURN', 0):,.0f}")
    net = row.get("TOTAL_NET_NEW", 0)
    c5.metric("Net New MRR YTD", f"${net:,.0f}", delta=f"{'▲' if net > 0 else '▼'}")

st.markdown("---")

if not wf_data.empty:
    wf_data.columns = [c.lower() for c in wf_data.columns]

    st.subheader("Monthly Revenue Waterfall — Stacked")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=wf_data["month_date"], y=wf_data["new_mrr"],         name="New MRR",     marker_color="#2ECC71"))
    fig.add_trace(go.Bar(x=wf_data["month_date"], y=wf_data["expansion_mrr"],   name="Expansion",   marker_color="#3498DB"))
    fig.add_trace(go.Bar(x=wf_data["month_date"], y=wf_data["contraction_mrr"], name="Contraction", marker_color="#E67E22"))
    fig.add_trace(go.Bar(x=wf_data["month_date"], y=wf_data["churn_mrr"],       name="Churn",       marker_color="#E74C3C"))
    fig.add_trace(go.Scatter(
        x=wf_data["month_date"], y=wf_data["net_new_mrr"],
        name="Net New MRR", line=dict(color="#F1C40F", width=3),
        mode="lines+markers",
    ))
    fig.update_layout(
        barmode="relative", template="plotly_dark", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis_title="Month", yaxis_title="MRR ($)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Net New MRR Trend")
    col1, col2 = st.columns([3, 1])
    with col1:
        net_fig = px.bar(
            wf_data, x="month_date", y="net_new_mrr",
            title="Net New MRR (Positive = Growth, Negative = Contraction)",
            template="plotly_dark", color="net_new_mrr",
            color_continuous_scale=["#E74C3C", "#F1C40F", "#2ECC71"],
            labels={"net_new_mrr": "Net New MRR ($)", "month_date": "Month"},
        )
        net_fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        net_fig.update_layout(height=300)
        st.plotly_chart(net_fig, use_container_width=True)

    with col2:
        st.markdown("### Quick Stats")
        positive_months = (wf_data["net_new_mrr"] > 0).sum()
        negative_months = (wf_data["net_new_mrr"] <= 0).sum()
        st.metric("Growth months",       positive_months)
        st.metric("Contraction months",  negative_months)
        st.metric("Best month Net MRR",  f"${wf_data['net_new_mrr'].max():,.0f}")
        st.metric("Worst month Net MRR", f"${wf_data['net_new_mrr'].min():,.0f}")

    with st.expander("🔍 View raw waterfall data"):
        st.dataframe(wf_data, use_container_width=True, hide_index=True)

else:
    st.info("No waterfall data found. Check that `revenue_waterfall` exists in GOLD schema.")