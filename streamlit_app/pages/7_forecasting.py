import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from utils.snowflake_connector import run_query
import io

st.set_page_config(page_title="Revenue Forecasting", page_icon="📈", layout="wide")
st.title("📈 Revenue Forecasting")
st.markdown("6-month MRR projection with Best / Base / Worst case scenarios.")

@st.cache_data(ttl=300)
def load_mrr_history():
    return run_query("""
        SELECT
            INVOICE_MONTH AS month_date,
            SUM(MRR) AS total_mrr
        FROM SAAS_REVENUE_DB.GOLD.mrr_monthly
        GROUP BY INVOICE_MONTH
        ORDER BY INVOICE_MONTH
    """)

with st.spinner("Loading MRR history..."):
    df = load_mrr_history()

if df.empty:
    st.error("No MRR data found.")
    st.stop()

df.columns = [c.lower() for c in df.columns]
df["month_date"] = pd.to_datetime(df["month_date"])
df = df.sort_values("month_date").reset_index(drop=True)
df["month_index"] = range(len(df))

st.sidebar.header("⚙️ Forecast Settings")
forecast_months  = st.sidebar.slider("Forecast months ahead", 3, 12, 6)
best_multiplier  = st.sidebar.slider("Best case growth boost %", 5, 30, 15)
worst_multiplier = st.sidebar.slider("Worst case growth reduction %", 5, 30, 15)

X = df["month_index"].values.reshape(-1, 1)
y = df["total_mrr"].values
model = LinearRegression()
model.fit(X, y)

last_index = int(df["month_index"].max())
last_date  = df["month_date"].max()

future_indices = list(range(last_index + 1, last_index + forecast_months + 1))
future_dates   = [last_date + pd.DateOffset(months=i) for i in range(1, forecast_months + 1)]

base_forecast  = [float(model.predict([[i]])[0]) for i in future_indices]
best_forecast  = [v * (1 + best_multiplier/100)  for v in base_forecast]
worst_forecast = [v * (1 - worst_multiplier/100) for v in base_forecast]

current_mrr   = float(df["total_mrr"].iloc[-1])
base_end_mrr  = base_forecast[-1]
best_end_mrr  = best_forecast[-1]
worst_end_mrr = worst_forecast[-1]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current MRR",  f"${current_mrr:,.0f}")
c2.metric("Base Case",    f"${base_end_mrr:,.0f}",
          f"{((base_end_mrr-current_mrr)/current_mrr*100):+.1f}%")
c3.metric("Best Case",    f"${best_end_mrr:,.0f}",
          f"{((best_end_mrr-current_mrr)/current_mrr*100):+.1f}%")
c4.metric("Worst Case",   f"${worst_end_mrr:,.0f}",
          f"{((worst_end_mrr-current_mrr)/current_mrr*100):+.1f}%",
          delta_color="inverse")

st.markdown("---")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["month_date"], y=df["total_mrr"],
    name="Historical MRR",
    line=dict(color="#00D4FF", width=3),
    mode="lines+markers"))
fig.add_trace(go.Scatter(
    x=future_dates, y=best_forecast,
    name="Best Case",
    line=dict(color="#2ECC71", width=2, dash="dash"),
    mode="lines+markers"))
fig.add_trace(go.Scatter(
    x=future_dates, y=base_forecast,
    name="Base Case",
    line=dict(color="#F1C40F", width=2, dash="dash"),
    mode="lines+markers"))
fig.add_trace(go.Scatter(
    x=future_dates, y=worst_forecast,
    name="Worst Case",
    line=dict(color="#E74C3C", width=2, dash="dash"),
    mode="lines+markers"))
fig.add_trace(go.Scatter(
    x=future_dates + future_dates[::-1],
    y=best_forecast + worst_forecast[::-1],
    fill="toself",
    fillcolor="rgba(241,196,15,0.1)",
    line=dict(color="rgba(255,255,255,0)"),
    name="Forecast Range"))
fig.update_layout(
    title="MRR Forecast — 3 Scenarios",
    template="plotly_dark", height=450,
    xaxis_title="Month", yaxis_title="MRR ($)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Forecast Table")
forecast_df = pd.DataFrame({
    "Month":      [d.strftime("%b %Y") for d in future_dates],
    "Worst Case": [f"${v:,.0f}" for v in worst_forecast],
    "Base Case":  [f"${v:,.0f}" for v in base_forecast],
    "Best Case":  [f"${v:,.0f}" for v in best_forecast],
})
st.dataframe(forecast_df, use_container_width=True, hide_index=True)

st.markdown("---")
export_df = pd.DataFrame({
    "Month":      [d.strftime("%b %Y") for d in future_dates],
    "Worst Case": worst_forecast,
    "Base Case":  base_forecast,
    "Best Case":  best_forecast,
})
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    export_df.to_excel(writer, index=False, sheet_name="Forecast")
st.download_button("📥 Download Forecast as Excel",
    data=buffer.getvalue(), file_name="mrr_forecast.xlsx",
    mime="application/vnd.ms-excel")