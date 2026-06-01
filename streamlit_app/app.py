"""
SaaS Revenue Intelligence Platform
Built by Krithesh Vinothkumar — MSc Data & Computational Science, UCD Dublin
"""

import streamlit as st

st.set_page_config(
    page_title="SaaS Revenue Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar branding ──────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 10px;'>
    <img src='https://img.icons8.com/fluency/48/combo-chart.png' width='40'/>
    <h3 style='margin: 5px 0; color: #00D4FF;'>Revenue Intelligence</h3>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**🏦 Data Source**")
st.sidebar.markdown("**Snowflake:** `tejxpcq-vw92165`")
st.sidebar.markdown("**Database:** `SAAS_REVENUE_DB`")
st.sidebar.markdown("**Schema:** `GOLD`")
st.sidebar.markdown("---")

st.sidebar.markdown("""
<div style='
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #00D4FF;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    margin-top: 10px;
'>
    <p style='color: #00D4FF; font-size: 13px; margin: 0; font-weight: bold;'>👨‍💻 Built by</p>
    <p style='color: white; font-size: 14px; margin: 4px 0; font-weight: bold;'>Krithesh Vinothkumar</p>
    <p style='color: #aaaaaa; font-size: 11px; margin: 0;'>MSc Data & Computational Science</p>
    <p style='color: #aaaaaa; font-size: 11px; margin: 0;'>University College Dublin 🇮🇪</p>
    <br/>
    <a href='https://linkedin.com/in/krithesh-analyst' target='_blank'
       style='color: #0077B5; font-size: 11px; text-decoration: none;'>
        🔗 LinkedIn
    </a>
    &nbsp;|&nbsp;
    <a href='https://github.com/krithesh19' target='_blank'
       style='color: #aaaaaa; font-size: 11px; text-decoration: none;'>
        🐙 GitHub
    </a>
</div>
""", unsafe_allow_html=True)

# ── Main page ─────────────────────────────────────────────────────────────────
st.title("📊 SaaS Revenue Intelligence Platform")
st.markdown("### Your AI-powered revenue analytics command centre")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Platform", "Snowflake", "GOLD schema")
with col2:
    st.metric("AI Engine", "LangChain", "Groq LLaMA")
with col3:
    st.metric("Dashboard Pages", "11", "Interactive")
with col4:
    st.metric("Finance KPIs", "12+", "Tracked")

st.markdown("---")

st.markdown("""
## 🏗️ Platform Architecture

Azure Blob  →  Snowflake RAW  →  dbt STAGING  →  dbt GOLD  →  Power BI
↓
Streamlit AI Layer
├── 💬 LangChain SQL Agent
├── 📈 MRR / ARR Analytics
├── 🔄 Churn Analysis
├── 💎 Customer LTV
├── 🌊 Revenue Waterfall
├── 📈 Revenue Forecasting
├── 📊 Budget vs Actuals
├── 💰 Unit Economics
├── 🔄 Cohort Analysis
└── ⚡ Quick Ratio & Rule of 40

## 📋 Gold Layer Tables
| Table | Rows | Description |
|---|---|---|
| `mrr_monthly` | 5,057 | Monthly Recurring Revenue by segment |
| `churn_analysis` | 500 | Churned customers, rates, and reasons |
| `customer_ltv` | 500 | Lifetime value scores per customer |
| `arr_summary` | 24 | Annual Recurring Revenue aggregated |
| `revenue_waterfall` | 47 | MRR movement analysis |
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='
    text-align: center;
    padding: 15px;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 10px;
    border: 1px solid #333;
'>
    <p style='color: #aaaaaa; font-size: 12px; margin: 0;'>
        📊 <b style='color: #00D4FF;'>SaaS Revenue Intelligence Platform</b>
        &nbsp;|&nbsp;
        Built by <b style='color: white;'>Krithesh Vinothkumar</b>
        &nbsp;|&nbsp;
        MSc Data & Computational Science, University College Dublin
        &nbsp;|&nbsp;
        <a href='https://krithesh-saas-platform.streamlit.app'
           style='color: #00D4FF; text-decoration: none;'>
           🚀 Live App
        </a>
        &nbsp;|&nbsp;
        <a href='https://github.com/krithesh19/saas-revenue-platform'
           style='color: #aaaaaa; text-decoration: none;'>
           🐙 GitHub
        </a>
        &nbsp;|&nbsp;
        <a href='https://linkedin.com/in/krithesh-analyst'
           style='color: #0077B5; text-decoration: none;'>
           🔗 LinkedIn
        </a>
    </p>
</div>
""", unsafe_allow_html=True)