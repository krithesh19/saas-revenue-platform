"""
streamlit_app/pages/11_quick_ratio.py
⚡ Quick Ratio & Rule of 40 — SaaS Health Metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.snowflake_connector import run_query
import io

st.set_page_config(page_title="Quick Ratio & Rule of 40", page_icon="⚡", layout="wide")
st.title("⚡ Quick Ratio & Rule of 40")
st.markdown("The two most important SaaS business health metrics used by investors and CFOs.")

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
def load_mrr():
    return run_query("""
        SELECT
            month_date,
            SUM(mrr_amount) AS total_mrr
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY month_date
        ORDER BY month_date
    """)

with st.spinner("Loading data..."):
    wf_df  = load_waterfall()
    mrr_df = load_mrr()

if wf_df.empty:
    st.error("No waterfall data found.")
    st.stop()

wf_df.columns  = [c.lower() for c in wf_df.columns]
mrr_df.columns = [c.lower() for c in mrr_df.columns]

wf_df["month_date"]  = pd.to_datetime(wf_df["month_date"])
mrr_df["month_date"] = pd.to_datetime(mrr_df["month_date"])

# ── Quick Ratio calculation ───────────────────────────────────────────────────
wf_df["quick_ratio"] = (
    (wf_df["new_mrr"] + wf_df["expansion_mrr"]) /
    (wf_df["churn_mrr"].abs() + wf_df["contraction_mrr"].abs())
).replace([np.inf, -np.inf], 0).fillna(0)

# ── Rule of 40 calculation ────────────────────────────────────────────────────
mrr_df["growth_rate"] = mrr_df["total_mrr"].pct_change() * 100

st.sidebar.header("⚙️ Rule of 40 Settings")
profit_margin = st.sidebar.slider(
    "Current profit margin %", -50, 50, -10,
    help="Negative = still investing in growth"
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Ratio Benchmarks:**")
st.sidebar.markdown("- Below 1: Shrinking")
st.sidebar.markdown("- 1-2: Slow growth")
st.sidebar.markdown("- 2-4: Healthy")
st.sidebar.markdown("- Above 4: Excellent")
st.sidebar.markdown("---")
st.sidebar.markdown("**Rule of 40 Benchmark:**")
st.sidebar.markdown("- Above 40: Healthy")
st.sidebar.markdown("- Below 40: Needs attention")

# ── KPIs ──────────────────────────────────────────────────────────────────────
avg_quick_ratio   = wf_df["quick_ratio"].mean()
latest_quick      = wf_df["quick_ratio"].iloc[-1]
avg_growth_rate   = mrr_df["growth_rate"].mean()
rule_of_40_score  = avg_growth_rate + profit_margin

def qr_status(qr):
    if qr >= 4:   return "🟢 Excellent"
    elif qr >= 2: return "🟡 Healthy"
    elif qr >= 1: return "🟠 Slow Growth"
    else:         return "🔴 Shrinking"

def r40_status(score):
    if score >= 40: return "🟢 Healthy"
    elif score >= 20: return "🟡 Watch"
    else: return "🔴 Needs Attention"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Quick Ratio",  f"{latest_quick:.2f}",  qr_status(latest_quick))
c2.metric("Avg Quick Ratio",     f"{avg_quick_ratio:.2f}", qr_status(avg_quick_ratio))
c3.metric("Avg MRR Growth Rate", f"{avg_growth_rate:.1f}%")
c4.metric("Rule of 40 Score",    f"{rule_of_40_score:.1f}",
          r40_status(rule_of_40_score),
          delta_color="normal" if rule_of_40_score >= 40 else "inverse")

st.markdown("---")

# ── Quick Ratio chart ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Quick Ratio Over Time")
    colors = ["#2ECC71" if qr >= 4 else "#F1C40F" if qr >= 2
              else "#E67E22" if qr >= 1 else "#E74C3C"
              for qr in wf_df["quick_ratio"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=wf_df["month_date"],
        y=wf_df["quick_ratio"],
        marker_color=colors,
        name="Quick Ratio",
    ))
    fig.add_hline(y=4, line_dash="dash", line_color="#2ECC71",
                  annotation_text="Excellent (4)", annotation_position="right")
    fig.add_hline(y=2, line_dash="dash", line_color="#F1C40F",
                  annotation_text="Healthy (2)", annotation_position="right")
    fig.add_hline(y=1, line_dash="dash", line_color="#E74C3C",
                  annotation_text="Minimum (1)", annotation_position="right")
    fig.update_layout(
        template="plotly_dark", height=380,
        yaxis_title="Quick Ratio",
        xaxis_title="Month",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Rule of 40 Gauge")
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rule_of_40_score,
        delta={"reference": 40},
        title={"text": "Rule of 40 Score"},
        gauge={
            "axis": {"range": [-50, 100]},
            "bar":  {"color": "#00D4FF"},
            "steps": [
                {"range": [-50, 0],  "color": "#E74C3C"},
                {"range": [0, 20],   "color": "#E67E22"},
                {"range": [20, 40],  "color": "#F1C40F"},
                {"range": [40, 100], "color": "#2ECC71"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 4},
                "thickness": 0.75,
                "value": 40,
            },
        },
    ))
    fig2.update_layout(
        template="plotly_dark", height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Quick Ratio breakdown ─────────────────────────────────────────────────────
st.subheader("Quick Ratio Components")
fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=wf_df["month_date"],
    y=wf_df["new_mrr"] + wf_df["expansion_mrr"],
    name="Inflow (New + Expansion)",
    marker_color="#2ECC71",
))
fig3.add_trace(go.Bar(
    x=wf_df["month_date"],
    y=-(wf_df["churn_mrr"].abs() + wf_df["contraction_mrr"].abs()),
    name="Outflow (Churn + Contraction)",
    marker_color="#E74C3C",
))
fig3.update_layout(
    barmode="relative",
    template="plotly_dark", height=320,
    title="MRR Inflow vs Outflow",
    xaxis_title="Month", yaxis_title="MRR ($)",
)
st.plotly_chart(fig3, use_container_width=True)

# ── Interpretation ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💡 What This Means")

if latest_quick >= 4:
    st.success(f"**Quick Ratio {latest_quick:.2f}** — Excellent! For every $1 lost to churn, "
               f"you're gaining ${latest_quick:.2f} from new and expansion revenue.")
elif latest_quick >= 2:
    st.info(f"**Quick Ratio {latest_quick:.2f}** — Healthy growth. "
            f"Focus on expanding existing accounts to push above 4.")
elif latest_quick >= 1:
    st.warning(f"**Quick Ratio {latest_quick:.2f}** — Slow growth. "
               f"New revenue barely covers churn losses.")
else:
    st.error(f"**Quick Ratio {latest_quick:.2f}** — Business is shrinking. "
             f"Churn is outpacing new revenue.")

if rule_of_40_score >= 40:
    st.success(f"**Rule of 40 Score: {rule_of_40_score:.1f}** — Healthy balance of "
               f"growth ({avg_growth_rate:.1f}%) and profitability ({profit_margin}%).")
else:
    st.warning(f"**Rule of 40 Score: {rule_of_40_score:.1f}** — Below 40 benchmark. "
               f"Need higher growth rate or improved margins.")

# ── Excel export ──────────────────────────────────────────────────────────────
st.markdown("---")
buffer = io.BytesIO()
export_df = wf_df[["month_date", "new_mrr", "expansion_mrr",
                    "churn_mrr", "contraction_mrr", "quick_ratio"]].copy()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    export_df.to_excel(writer, index=False, sheet_name="Quick Ratio")
st.download_button(
    label="📥 Download as Excel",
    data=buffer.getvalue(),
    file_name="quick_ratio.xlsx",
    mime="application/vnd.ms-excel",
)