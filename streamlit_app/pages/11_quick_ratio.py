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
            INVOICE_MONTH,
            MRR_MOVEMENT_TYPE,
            TOTAL_MRR,
            MRR_CHANGE
        FROM SAAS_REVENUE_DB.GOLD.revenue_waterfall
        ORDER BY INVOICE_MONTH
    """)

@st.cache_data(ttl=300)
def load_mrr():
    return run_query("""
        SELECT
            INVOICE_MONTH AS month_date,
            SUM(MRR) AS total_mrr
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY INVOICE_MONTH
        ORDER BY INVOICE_MONTH
    """)

with st.spinner("Loading data..."):
    wf_df  = load_waterfall()
    mrr_df = load_mrr()

if wf_df.empty:
    st.error("No waterfall data found.")
    st.stop()

wf_df.columns  = [c.lower() for c in wf_df.columns]
mrr_df.columns = [c.lower() for c in mrr_df.columns]

wf_df["invoice_month"] = pd.to_datetime(wf_df["invoice_month"])
mrr_df["month_date"]   = pd.to_datetime(mrr_df["month_date"])

# ── Pivot waterfall by movement type ─────────────────────────────────────────
pivot = wf_df.pivot_table(
    index="invoice_month",
    columns="mrr_movement_type",
    values="total_mrr",
    aggfunc="sum"
).fillna(0).reset_index()

pivot.columns = [str(c).lower().replace(" ", "_") for c in pivot.columns]

# ── Try to find new/expansion/churn columns ───────────────────────────────────
all_cols = list(pivot.columns)
new_col       = next((c for c in all_cols if "new" in c), None)
expansion_col = next((c for c in all_cols if "expansion" in c or "upgrade" in c), None)
churn_col     = next((c for c in all_cols if "churn" in c or "cancel" in c), None)
contract_col  = next((c for c in all_cols if "contract" in c or "downgrade" in c), None)

# ── Quick Ratio ───────────────────────────────────────────────────────────────
if new_col and churn_col:
    inflow  = pivot[new_col] + (pivot[expansion_col] if expansion_col else 0)
    outflow = pivot[churn_col].abs() + (pivot[contract_col].abs() if contract_col else 0)
    pivot["quick_ratio"] = (inflow / outflow.replace(0, np.nan)).fillna(0)
else:
    pivot["quick_ratio"] = 0

mrr_df["growth_rate"] = mrr_df["total_mrr"].pct_change() * 100

st.sidebar.header("⚙️ Rule of 40 Settings")
profit_margin = st.sidebar.slider("Current profit margin %", -50, 50, -10)
st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Ratio Benchmarks:**")
st.sidebar.markdown("- Below 1: Shrinking")
st.sidebar.markdown("- 1-2: Slow growth")
st.sidebar.markdown("- 2-4: Healthy")
st.sidebar.markdown("- Above 4: Excellent")

avg_quick_ratio  = pivot["quick_ratio"].mean()
latest_quick     = pivot["quick_ratio"].iloc[-1]
avg_growth_rate  = mrr_df["growth_rate"].mean()
rule_of_40_score = avg_growth_rate + profit_margin

def qr_status(qr):
    if qr >= 4:    return "🟢 Excellent"
    elif qr >= 2:  return "🟡 Healthy"
    elif qr >= 1:  return "🟠 Slow Growth"
    else:          return "🔴 Shrinking"

def r40_status(score):
    if score >= 40:   return "🟢 Healthy"
    elif score >= 20: return "🟡 Watch"
    else:             return "🔴 Needs Attention"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Quick Ratio",  f"{latest_quick:.2f}", qr_status(latest_quick))
c2.metric("Avg Quick Ratio",     f"{avg_quick_ratio:.2f}", qr_status(avg_quick_ratio))
c3.metric("Avg MRR Growth Rate", f"{avg_growth_rate:.1f}%")
c4.metric("Rule of 40 Score",    f"{rule_of_40_score:.1f}",
          r40_status(rule_of_40_score),
          delta_color="normal" if rule_of_40_score >= 40 else "inverse")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Quick Ratio Over Time")
    colors = ["#2ECC71" if qr >= 4 else "#F1C40F" if qr >= 2
              else "#E67E22" if qr >= 1 else "#E74C3C"
              for qr in pivot["quick_ratio"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pivot["invoice_month"], y=pivot["quick_ratio"],
        marker_color=colors, name="Quick Ratio"))
    fig.add_hline(y=4, line_dash="dash", line_color="#2ECC71",
                  annotation_text="Excellent (4)")
    fig.add_hline(y=2, line_dash="dash", line_color="#F1C40F",
                  annotation_text="Healthy (2)")
    fig.add_hline(y=1, line_dash="dash", line_color="#E74C3C",
                  annotation_text="Minimum (1)")
    fig.update_layout(template="plotly_dark", height=380,
                      yaxis_title="Quick Ratio", xaxis_title="Month")
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
                "thickness": 0.75, "value": 40,
            },
        },
    ))
    fig2.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("MRR by Movement Type")
fig3 = px.bar(
    wf_df, x="invoice_month", y="total_mrr",
    color="mrr_movement_type",
    title="MRR Breakdown by Movement Type",
    template="plotly_dark",
    labels={"total_mrr": "MRR ($)", "invoice_month": "Month"},
)
fig3.update_layout(height=320)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("💡 What This Means")
if latest_quick >= 4:
    st.success(f"**Quick Ratio {latest_quick:.2f}** — Excellent growth efficiency!")
elif latest_quick >= 2:
    st.info(f"**Quick Ratio {latest_quick:.2f}** — Healthy growth.")
elif latest_quick >= 1:
    st.warning(f"**Quick Ratio {latest_quick:.2f}** — Slow growth.")
else:
    st.error(f"**Quick Ratio {latest_quick:.2f}** — Business is shrinking!")

if rule_of_40_score >= 40:
    st.success(f"**Rule of 40: {rule_of_40_score:.1f}** ✅ Healthy!")
else:
    st.warning(f"**Rule of 40: {rule_of_40_score:.1f}** — Below 40 benchmark.")

st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    pivot.to_excel(writer, index=False, sheet_name="Quick Ratio")
st.download_button("📥 Download as Excel",
    data=buffer.getvalue(), file_name="quick_ratio.xlsx",
    mime="application/vnd.ms-excel")