"""
streamlit_app/pages/9_unit_economics.py
💰 Unit Economics — CAC, LTV:CAC Ratio, Payback Period
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.snowflake_connector import run_query
import io

st.set_page_config(page_title="Unit Economics", page_icon="💰", layout="wide")
st.title("💰 Unit Economics")
st.markdown("CAC, LTV:CAC Ratio, and Payback Period — the fundamental health metrics of your SaaS business.")

@st.cache_data(ttl=300)
def load_ltv_data():
    return run_query("""
        SELECT
            customer_segment,
            COUNT(*)                        AS total_customers,
            ROUND(AVG(predicted_ltv), 0)    AS avg_ltv,
            ROUND(SUM(predicted_ltv), 0)    AS total_ltv
        FROM SAAS_REVENUE_DB.GOLD.customer_ltv
        GROUP BY customer_segment
        ORDER BY avg_ltv DESC
    """)

@st.cache_data(ttl=300)
def load_mrr_data():
    return run_query("""
        SELECT
            customer_segment,
            ROUND(AVG(mrr_amount), 2) AS avg_mrr
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY customer_segment
    """)

@st.cache_data(ttl=300)
def load_churn_rate():
    return run_query("""
        SELECT
            customer_segment,
            COUNT(*) AS churned_customers
        FROM SAAS_REVENUE_DB.GOLD.churn_analysis
        GROUP BY customer_segment
    """)

with st.spinner("Loading unit economics data..."):
    ltv_df   = load_ltv_data()
    mrr_df   = load_mrr_data()
    churn_df = load_churn_rate()

# ── Sidebar — CAC inputs ──────────────────────────────────────────────────────
st.sidebar.header("⚙️ CAC Settings")
st.sidebar.markdown("Enter your monthly sales & marketing spend per segment:")

segments = ["Enterprise", "Mid-Market", "SMB"] if ltv_df.empty else \
    [str(s) for s in ltv_df["CUSTOMER_SEGMENT"].tolist() if s] \
    if "CUSTOMER_SEGMENT" in ltv_df.columns else ["Enterprise", "Mid-Market", "SMB"]

cac_inputs = {}
for seg in segments:
    cac_inputs[seg] = st.sidebar.number_input(
        f"{seg} CAC ($)", min_value=100, max_value=50000,
        value={"Enterprise": 5000, "Mid-Market": 2000, "SMB": 500}.get(seg, 1000),
        step=100,
    )

st.sidebar.markdown("---")
st.sidebar.markdown("**Healthy benchmarks:**")
st.sidebar.markdown("- LTV:CAC ratio > 3:1")
st.sidebar.markdown("- Payback period < 12 months")
st.sidebar.markdown("- Churn rate < 5% monthly")

# ── Build unit economics table ────────────────────────────────────────────────
if not ltv_df.empty:
    ltv_df.columns = [c.lower() for c in ltv_df.columns]

    rows = []
    for _, row in ltv_df.iterrows():
        seg      = str(row.get("customer_segment", "Unknown"))
        avg_ltv  = float(row.get("avg_ltv", 0))
        cac      = cac_inputs.get(seg, 1000)
        ltv_cac  = avg_ltv / cac if cac > 0 else 0

        avg_mrr = 100
        if not mrr_df.empty:
            mrr_df.columns = [c.lower() for c in mrr_df.columns]
            mrr_row = mrr_df[mrr_df["customer_segment"] == seg]
            if not mrr_row.empty:
                avg_mrr = float(mrr_row["avg_mrr"].iloc[0])

        payback = cac / avg_mrr if avg_mrr > 0 else 0

        def health(ratio):
            if ratio >= 3:   return "🟢 Healthy"
            elif ratio >= 1: return "🟡 Marginal"
            else:            return "🔴 Unhealthy"

        def payback_health(months):
            if months <= 12: return "🟢 Good"
            elif months <= 24: return "🟡 Watch"
            else:            return "🔴 Too Long"

        rows.append({
            "Segment":        seg,
            "Avg LTV ($)":    f"${avg_ltv:,.0f}",
            "CAC ($)":        f"${cac:,.0f}",
            "LTV:CAC Ratio":  f"{ltv_cac:.1f}:1",
            "Ratio Health":   health(ltv_cac),
            "Avg MRR ($)":    f"${avg_mrr:,.0f}",
            "Payback (months)": f"{payback:.1f}",
            "Payback Health": payback_health(payback),
            "_ltv_cac":       ltv_cac,
            "_payback":       payback,
        })

    econ_df = pd.DataFrame(rows)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    avg_ratio   = econ_df["_ltv_cac"].mean()
    avg_payback = econ_df["_payback"].mean()
    healthy_segs = (econ_df["_ltv_cac"] >= 3).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg LTV:CAC Ratio",    f"{avg_ratio:.1f}:1",
              "✅ Healthy" if avg_ratio >= 3 else "⚠️ Below benchmark")
    c2.metric("Avg Payback Period",   f"{avg_payback:.1f} months",
              "✅ Good" if avg_payback <= 12 else "⚠️ Too long")
    c3.metric("Healthy Segments",     f"{healthy_segs}/{len(econ_df)}")
    c4.metric("Benchmark LTV:CAC",    "3:1 minimum")

    st.markdown("---")

    # ── LTV:CAC Chart ─────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("LTV:CAC Ratio by Segment")
        colors = ["#2ECC71" if r >= 3 else "#E67E22" if r >= 1 else "#E74C3C"
                  for r in econ_df["_ltv_cac"]]
        fig = go.Figure(go.Bar(
            x=econ_df["Segment"],
            y=econ_df["_ltv_cac"],
            marker_color=colors,
            text=[f"{r:.1f}:1" for r in econ_df["_ltv_cac"]],
            textposition="outside",
        ))
        fig.add_hline(y=3, line_dash="dash", line_color="#F1C40F",
                      annotation_text="3:1 Benchmark", annotation_position="right")
        fig.update_layout(
            template="plotly_dark", height=350,
            yaxis_title="LTV:CAC Ratio",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Payback Period by Segment")
        pb_colors = ["#2ECC71" if p <= 12 else "#E67E22" if p <= 24 else "#E74C3C"
                     for p in econ_df["_payback"]]
        fig2 = go.Figure(go.Bar(
            x=econ_df["Segment"],
            y=econ_df["_payback"],
            marker_color=pb_colors,
            text=[f"{p:.1f}m" for p in econ_df["_payback"]],
            textposition="outside",
        ))
        fig2.add_hline(y=12, line_dash="dash", line_color="#F1C40F",
                       annotation_text="12 Month Benchmark", annotation_position="right")
        fig2.update_layout(
            template="plotly_dark", height=350,
            yaxis_title="Payback Period (Months)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Full table ────────────────────────────────────────────────────────────
    st.subheader("📋 Full Unit Economics Table")
    display_cols = ["Segment", "Avg LTV ($)", "CAC ($)", "LTV:CAC Ratio",
                    "Ratio Health", "Avg MRR ($)", "Payback (months)", "Payback Health"]
    st.dataframe(econ_df[display_cols], use_container_width=True, hide_index=True)

    # ── Interpretation ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("💡 What This Means")
    for _, row in econ_df.iterrows():
        ratio = row["_ltv_cac"]
        if ratio >= 3:
            st.success(f"**{row['Segment']}** — LTV:CAC of {row['LTV:CAC Ratio']} is healthy. "
                      f"For every $1 spent acquiring a customer, you get ${ratio:.1f} back.")
        elif ratio >= 1:
            st.warning(f"**{row['Segment']}** — LTV:CAC of {row['LTV:CAC Ratio']} is marginal. "
                      f"Consider reducing CAC or improving retention.")
        else:
            st.error(f"**{row['Segment']}** — LTV:CAC of {row['LTV:CAC Ratio']} is unhealthy. "
                    f"Losing money on customer acquisition.")

    # ── Excel export ──────────────────────────────────────────────────────────
    st.markdown("---")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        econ_df[display_cols].to_excel(writer, index=False, sheet_name="Unit Economics")
    st.download_button(
        label="📥 Download as Excel",
        data=buffer.getvalue(),
        file_name="unit_economics.xlsx",
        mime="application/vnd.ms-excel",
    )
else:
    st.info("No LTV data available. Run dbt models first.")