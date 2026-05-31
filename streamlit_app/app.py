"""
SaaS Revenue Intelligence Platform
Day 10 — Streamlit + LangChain AI Layer
Main application entry point
"""

import streamlit as st

st.set_page_config(
    page_title="SaaS Revenue Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar nav ──────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
st.sidebar.title("Revenue Intelligence")
st.sidebar.markdown("---")

pages = {
    "🏠 Overview":           "pages/1_overview.py",
    "💬 AI Revenue Analyst": "pages/2_ai_analyst.py",
    "📈 MRR & ARR":          "pages/3_mrr_arr.py",
    "🔄 Churn Analysis":     "pages/4_churn.py",
    "💎 Customer LTV":       "pages/5_ltv.py",
    "🌊 Revenue Waterfall":  "pages/6_waterfall.py",
}

st.sidebar.markdown("### Navigation")
for name in pages:
    st.sidebar.markdown(f"[{name}](#)")

st.sidebar.markdown("---")
st.sidebar.markdown("**Snowflake:** `tejxpcq-vw92165`")
st.sidebar.markdown("**Database:** `SAAS_REVENUE_DB`")
st.sidebar.markdown("**Schema:** `GOLD`")

# ── Home page ────────────────────────────────────────────────────────────────
st.title("📊 SaaS Revenue Intelligence Platform")
st.markdown("### Your AI-powered revenue analytics command centre")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Platform", "Snowflake", "GOLD schema")
with col2:
    st.metric("AI Engine", "LangChain", "GPT-4o / Claude")
with col3:
    st.metric("Tables", "5", "Gold layer")
with col4:
    st.metric("Day", "10 / 14", "In progress")

st.markdown("---")

st.markdown("""
## 🗺️ Platform Architecture

```
Azure Blob  →  Snowflake RAW  →  dbt STAGING  →  dbt GOLD  →  Power BI
                                                         ↓
                                              Streamlit AI Layer  (Day 10)
                                              ├── LangChain SQL Agent
                                              ├── GPT-4o natural language Q&A
                                              ├── MRR / ARR visualisations
                                              ├── Churn & LTV dashboards
                                              └── Revenue waterfall charts
```

## 📋 Gold Layer Tables
| Table | Description |
|---|---|
| `mrr_monthly` | Monthly Recurring Revenue by cohort & product |
| `arr_summary` | Annual Recurring Revenue aggregated |
| `churn_analysis` | Churned customers, rates, and reasons |
| `customer_ltv` | Lifetime value scores per customer |
| `revenue_waterfall` | New / Expansion / Contraction / Churn breakdown |

## 🚀 Quick Start
1. Set your API keys in `.env` (see `README_DAY10.md`)
2. Run: `streamlit run streamlit_app/app.py`
3. Navigate to **💬 AI Revenue Analyst** to ask natural-language questions
""")
