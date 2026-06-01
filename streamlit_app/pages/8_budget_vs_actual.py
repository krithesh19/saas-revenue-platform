import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.snowflake_connector import run_query
import io

st.set_page_config(page_title="Budget vs Actuals", page_icon="📊", layout="wide")
st.title("📊 Budget vs Actuals")
st.markdown("Compare planned revenue against actuals with variance analysis and RAG status.")

@st.cache_data(ttl=300)
def load_actuals():
    return run_query("""
        SELECT
            INVOICE_MONTH AS month_date,
            SUM(MRR) AS actual_mrr
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY INVOICE_MONTH
        ORDER BY INVOICE_MONTH
    """)

with st.spinner("Loading actuals..."):
    df = load_actuals()

if df.empty:
    st.error("No MRR data found.")
    st.stop()

df.columns = [c.lower() for c in df.columns]
df["month_date"] = pd.to_datetime(df["month_date"])
df = df.sort_values("month_date").reset_index(drop=True)

st.sidebar.header("⚙️ Budget Settings")
budget_method = st.sidebar.radio(
    "Budget method",
    ["Auto (5% growth target)", "Manual (flat budget)"]
)

if budget_method == "Auto (5% growth target)":
    growth_target = st.sidebar.slider("Monthly growth target %", 1, 20, 5)
    first_budget  = df["actual_mrr"].iloc[0]
    df["budget_mrr"] = [first_budget * ((1 + growth_target/100) ** i) for i in range(len(df))]
else:
    flat_budget = st.sidebar.number_input(
        "Flat monthly budget ($)", min_value=1000,
        value=int(df["actual_mrr"].mean()), step=1000)
    df["budget_mrr"] = flat_budget

df["variance"]     = df["actual_mrr"] - df["budget_mrr"]
df["variance_pct"] = (df["variance"] / df["budget_mrr"] * 100).round(1)

def rag_status(pct):
    if pct >= -5:   return "🟢 Green"
    elif pct >= -10: return "🟡 Amber"
    else:            return "🔴 Red"

df["rag"] = df["variance_pct"].apply(rag_status)

total_actual   = df["actual_mrr"].sum()
total_budget   = df["budget_mrr"].sum()
total_variance = total_actual - total_budget
total_var_pct  = (total_variance / total_budget * 100)
green_months   = (df["rag"] == "🟢 Green").sum()
red_months     = (df["rag"] == "🔴 Red").sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Actual MRR",    f"${total_actual:,.0f}")
c2.metric("Total Budget MRR",    f"${total_budget:,.0f}")
c3.metric("Total Variance",      f"${total_variance:,.0f}",
          f"{total_var_pct:+.1f}%",
          delta_color="normal" if total_variance >= 0 else "inverse")
c4.metric("🟢 On Track Months",  green_months)
c5.metric("🔴 Off Track Months", red_months)

st.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["month_date"], y=df["budget_mrr"],
        name="Budget", marker_color="#3498DB", opacity=0.7))
    fig.add_trace(go.Scatter(
        x=df["month_date"], y=df["actual_mrr"],
        name="Actual", line=dict(color="#2ECC71", width=3),
        mode="lines+markers"))
    fig.update_layout(title="Actual vs Budget MRR",
        template="plotly_dark", height=400,
        xaxis_title="Month", yaxis_title="MRR ($)",
        legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("RAG Summary")
    rag_counts = df["rag"].value_counts().reset_index()
    rag_counts.columns = ["Status", "Months"]
    st.dataframe(rag_counts, use_container_width=True, hide_index=True)
    st.markdown("🟢 Within 5% of budget")
    st.markdown("🟡 5-10% below budget")
    st.markdown("🔴 More than 10% below budget")

st.subheader("Monthly Variance")
colors_list = ["#2ECC71" if v >= 0 else "#E74C3C" for v in df["variance"]]
fig2 = go.Figure(go.Bar(
    x=df["month_date"], y=df["variance"],
    marker_color=colors_list, name="Variance"))
fig2.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
fig2.update_layout(title="Monthly Variance (Actual - Budget)",
    template="plotly_dark", height=300,
    xaxis_title="Month", yaxis_title="Variance ($)")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📋 Full Variance Table")
display_df = df[["month_date","actual_mrr","budget_mrr","variance","variance_pct","rag"]].copy()
display_df["month_date"]   = display_df["month_date"].dt.strftime("%b %Y")
display_df["actual_mrr"]   = display_df["actual_mrr"].apply(lambda x: f"${x:,.0f}")
display_df["budget_mrr"]   = display_df["budget_mrr"].apply(lambda x: f"${x:,.0f}")
display_df["variance"]     = display_df["variance"].apply(lambda x: f"${x:,.0f}")
display_df["variance_pct"] = display_df["variance_pct"].apply(lambda x: f"{x:+.1f}%")
display_df.columns = ["Month","Actual MRR","Budget MRR","Variance","Variance %","RAG Status"]
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Budget vs Actuals")
st.download_button("📥 Download as Excel",
    data=buffer.getvalue(), file_name="budget_vs_actuals.xlsx",
    mime="application/vnd.ms-excel")