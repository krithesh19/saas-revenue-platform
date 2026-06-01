"""
SaaS Revenue Intelligence Platform
Built by Kritheshvar Vinothkumar — MSc Data & Computational Science, UCD Dublin
"""

import streamlit as st

st.set_page_config(
    page_title="SaaS Revenue Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:10px 0;'>
    <img src='https://img.icons8.com/fluency/48/combo-chart.png' width='45'/>
    <h3 style='margin:6px 0 2px;color:#00D4FF;font-size:16px;'>Revenue Intelligence</h3>
    <p style='color:#888;font-size:11px;margin:0;'>AI-Powered Analytics Platform</p>
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
    background:linear-gradient(135deg,#0f3460,#1a1a2e);
    border:1px solid #00D4FF;
    border-radius:10px;
    padding:14px;
    text-align:center;
'>
    <p style='color:#00D4FF;font-size:12px;margin:0 0 4px;font-weight:bold;letter-spacing:1px;'>👨‍💻 BUILT BY</p>
    <p style='color:white;font-size:15px;margin:0 0 2px;font-weight:bold;'>Kritheshvar Vinothkumar</p>
    <p style='color:#aaa;font-size:10px;margin:0 0 2px;'>MSc Data & Computational Science</p>
    <p style='color:#aaa;font-size:10px;margin:0 0 10px;'>University College Dublin 🇮🇪</p>
    <div style='display:flex;justify-content:center;gap:10px;'>
        <a href='https://linkedin.com/in/krithesh-analyst' target='_blank'
           style='background:#0077B5;color:white;padding:4px 10px;border-radius:5px;
                  font-size:10px;text-decoration:none;font-weight:bold;'>LinkedIn</a>
        <a href='https://github.com/krithesh19' target='_blank'
           style='background:#333;color:white;padding:4px 10px;border-radius:5px;
                  font-size:10px;text-decoration:none;font-weight:bold;'>GitHub</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='
    background:linear-gradient(135deg,#0f3460,#1a1a2e);
    border-radius:15px;padding:30px;margin-bottom:20px;
    border:1px solid #00D4FF;text-align:center;
'>
    <h1 style='color:white;margin:0 0 8px;font-size:36px;'>
        📊 SaaS Revenue Intelligence Platform
    </h1>
    <p style='color:#aaa;margin:0 0 15px;font-size:16px;'>
        End-to-end Data Engineering + Finance Analytics + AI
    </p>
    <div style='display:flex;justify-content:center;gap:10px;flex-wrap:wrap;'>
        <a href='https://krithesh-saas-platform.streamlit.app' target='_blank'
           style='background:#FF4B4B;color:white;padding:6px 16px;border-radius:20px;
                  text-decoration:none;font-size:12px;font-weight:bold;'>🚀 Live App</a>
        <a href='https://github.com/krithesh19/saas-revenue-platform' target='_blank'
           style='background:#333;color:white;padding:6px 16px;border-radius:20px;
                  text-decoration:none;font-size:12px;font-weight:bold;'>🐙 GitHub</a>
        <a href='https://linkedin.com/in/krithesh-analyst' target='_blank'
           style='background:#0077B5;color:white;padding:6px 16px;border-radius:20px;
                  text-decoration:none;font-size:12px;font-weight:bold;'>🔗 LinkedIn</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Platform",        "Snowflake",  "GOLD schema")
c2.metric("AI Engine",       "LangChain",  "Groq LLaMA")
c3.metric("Dashboard Pages", "11",         "Interactive")
c4.metric("Finance KPIs",    "12+",        "Tracked")

st.markdown("---")

# ── Architecture ──────────────────────────────────────────────────────────────
st.markdown("## 🏗️ Platform Architecture")

arch_html = """
<div style='background:linear-gradient(135deg,#1a1a2e,#0f3460);border-radius:12px;padding:25px;border:1px solid #00D4FF;margin:10px 0 20px;text-align:center;'>
    <div style='display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:15px;'>
        <div style='background:#0f3460;border-radius:10px;padding:12px 18px;border:1px solid #00D4FF;min-width:90px;'>
            <div style='font-size:26px;'>☁️</div>
            <div style='color:#00D4FF;font-weight:bold;font-size:12px;margin-top:4px;'>Azure Blob</div>
            <div style='color:#888;font-size:10px;'>Data Lake</div>
        </div>
        <div style='color:#00D4FF;font-size:22px;font-weight:bold;'>→</div>
        <div style='background:#0f3460;border-radius:10px;padding:12px 18px;border:1px solid #29B5E8;min-width:90px;'>
            <div style='font-size:26px;'>🏔️</div>
            <div style='color:#29B5E8;font-weight:bold;font-size:12px;margin-top:4px;'>Snowflake</div>
            <div style='color:#888;font-size:10px;'>RAW Schema</div>
        </div>
        <div style='color:#00D4FF;font-size:22px;font-weight:bold;'>→</div>
        <div style='background:#0f3460;border-radius:10px;padding:12px 18px;border:1px solid #FF694B;min-width:90px;'>
            <div style='font-size:26px;'>🔧</div>
            <div style='color:#FF694B;font-weight:bold;font-size:12px;margin-top:4px;'>dbt Core</div>
            <div style='color:#888;font-size:10px;'>GOLD Models</div>
        </div>
        <div style='color:#00D4FF;font-size:22px;font-weight:bold;'>→</div>
        <div style='background:#0f3460;border-radius:10px;padding:12px 18px;border:1px solid #F2C811;min-width:90px;'>
            <div style='font-size:26px;'>📊</div>
            <div style='color:#F2C811;font-weight:bold;font-size:12px;margin-top:4px;'>Power BI</div>
            <div style='color:#888;font-size:10px;'>Dashboard</div>
        </div>
        <div style='color:#00D4FF;font-size:22px;font-weight:bold;'>→</div>
        <div style='background:#0f3460;border-radius:10px;padding:12px 18px;border:1px solid #FF4B4B;min-width:90px;'>
            <div style='font-size:26px;'>🤖</div>
            <div style='color:#FF4B4B;font-weight:bold;font-size:12px;margin-top:4px;'>Streamlit AI</div>
            <div style='color:#888;font-size:10px;'>11 Pages</div>
        </div>
    </div>
    <p style='color:#888;font-size:11px;margin:0;'>⚙️ GitHub Actions CI/CD — Automated dbt tests on every push to main</p>
</div>
"""
st.markdown(arch_html, unsafe_allow_html=True)

# ── Gold Tables ───────────────────────────────────────────────────────────────
st.markdown("## 📋 Gold Layer Tables")

tables_data = [
    ("📈", "mrr_monthly",       "5,057", "MRR by segment"),
    ("🔄", "churn_analysis",    "500",   "Churn & lost MRR"),
    ("💎", "customer_ltv",      "500",   "LTV per customer"),
    ("📊", "arr_summary",       "24",    "ARR by year"),
    ("🌊", "revenue_waterfall", "47",    "MRR movement"),
]

c1, c2, c3, c4, c5 = st.columns(5)
for col, (icon, name, rows, desc) in zip([c1, c2, c3, c4, c5], tables_data):
    col.markdown(f"""
    <div style='background:linear-gradient(135deg,#0f3460,#1a1a2e);border-radius:10px;
                padding:15px;text-align:center;border:1px solid #333;height:120px;'>
        <div style='font-size:24px;'>{icon}</div>
        <div style='color:#00D4FF;font-size:11px;font-weight:bold;margin:4px 0;'>{name}</div>
        <div style='color:white;font-size:18px;font-weight:bold;'>{rows}</div>
        <div style='color:#888;font-size:10px;'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Navigation cards ──────────────────────────────────────────────────────────
st.markdown("## 🗺️ Navigation Guide")

pages = [
    ("🏠", "Overview",           "Live Snowflake connection + snapshot KPIs"),
    ("💬", "AI Revenue Analyst", "Ask questions in plain English — AI queries Snowflake"),
    ("📈", "MRR & ARR",          "Revenue trends, growth rates, segment breakdown"),
    ("🔄", "Churn Analysis",     "Churn by month, reason, and customer segment"),
    ("💎", "Customer LTV",       "LTV distribution, cohort chart, top customers"),
    ("🌊", "Revenue Waterfall",  "MRR movement — New vs Retained revenue"),
    ("📈", "Forecasting",        "6-month ML projection — Best/Base/Worst case"),
    ("📊", "Budget vs Actuals",  "Variance analysis with RAG traffic-light status"),
    ("💰", "Unit Economics",     "CAC, LTV:CAC ratio, Payback period by segment"),
    ("🔄", "Cohort Analysis",    "LTV heatmap by acquisition cohort and segment"),
    ("⚡", "Quick Ratio",        "Quick Ratio and Rule of 40 — investor metrics"),
]

cols = st.columns(3)
for i, (icon, name, desc) in enumerate(pages):
    with cols[i % 3]:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1a1a2e,#0f3460);border-radius:10px;
                    padding:15px;margin-bottom:10px;border:1px solid #333;
                    border-left:3px solid #00D4FF;'>
            <p style='margin:0;font-size:14px;color:white;font-weight:bold;'>{icon} {name}</p>
            <p style='margin:4px 0 0;font-size:11px;color:#888;'>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;padding:20px;background:linear-gradient(135deg,#1a1a2e,#0f3460);
            border-radius:12px;border:1px solid #333;'>
    <p style='color:white;font-size:14px;margin:0 0 6px;font-weight:bold;'>
        📊 SaaS Revenue Intelligence Platform
    </p>
    <p style='color:#aaa;font-size:12px;margin:0 0 10px;'>
        Built by <b style='color:white;'>Kritheshvar Vinothkumar</b>
        &nbsp;|&nbsp; MSc Data & Computational Science, University College Dublin
    </p>
    <div style='display:flex;justify-content:center;gap:15px;flex-wrap:wrap;'>
        <a href='https://krithesh-saas-platform.streamlit.app'
           style='color:#FF4B4B;text-decoration:none;font-size:12px;'>🚀 Live App</a>
        <a href='https://github.com/krithesh19/saas-revenue-platform'
           style='color:#aaa;text-decoration:none;font-size:12px;'>🐙 GitHub</a>
        <a href='https://linkedin.com/in/krithesh-analyst'
           style='color:#0077B5;text-decoration:none;font-size:12px;'>🔗 LinkedIn</a>
        <a href='https://krithesh-analyst.netlify.app'
           style='color:#00C853;text-decoration:none;font-size:12px;'>🌐 Portfolio</a>
    </div>
</div>
""", unsafe_allow_html=True)