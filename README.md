📊 SaaS Revenue Intelligence Platform
An end-to-end data engineering and AI analytics platform simulating real-world SaaS revenue tracking — built to demonstrate production-grade data skills for finance and analytics roles.

🏗️ Architecture
Azure Blob Storage → Snowflake RAW → dbt STAGING → dbt GOLD → Power BI → Streamlit + LangChain AI

🛠️ Tech Stack
LayerTechnologyCloud StorageAzure Blob StorageData WarehouseSnowflakeTransformationdbt CoreVisualisationPower BIAI LayerStreamlit + LangChain + Groq LLaMACI/CDGitHub ActionsLanguagePython, SQL

📋 Gold Layer Tables
TableRowsDescriptionmrr_monthly5,057Monthly Recurring Revenue by segmentchurn_analysis500Churned customers and lost MRRcustomer_ltv500Predicted lifetime value per customerarr_summary24Annual Recurring Revenue by yearrevenue_waterfall47New / Expansion / Contraction / Churn MRR

🤖 AI Revenue Analyst
Natural language querying of Snowflake data using LangChain + Groq LLaMA. Ask questions like:

"What was our MRR growth rate over the last 6 months?"
"Which customer segment has the highest churn rate?"
"Show me the top 10 customers by lifetime value."
"Break down our revenue waterfall for the last quarter."


🚀 How to Run
1. Clone the repo
git clone https://github.com/krithesh19/saas-revenue-platform.git
2. Install dependencies
pip install -r requirements_day10.txt
3. Add credentials to .env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=SAAS_WH
SNOWFLAKE_DATABASE=SAAS_REVENUE_DB
SNOWFLAKE_SCHEMA=GOLD
GROQ_API_KEY=your_groq_key
4. Run dbt models
cd saas_revenue_dbt
dbt run
5. Launch Streamlit app
cd ..
streamlit run streamlit_app/app.py

📁 Project Structure
saas-revenue-platform/
├── etl/                    # Python ingestion scripts
├── saas_revenue_dbt/       # dbt models (staging + gold)
├── streamlit_app/          # AI dashboard
│   ├── pages/              # MRR, Churn, LTV, Waterfall
│   └── utils/              # Snowflake connector + LangChain agent
├── .github/workflows/      # CI/CD pipeline
└── powerbi/                # Power BI dashboard

✅ What This Demonstrates

Cloud data ingestion with Azure Blob Storage
Snowflake data warehouse design and optimisation
dbt layered transformation (RAW → STAGING → GOLD)
Power BI dashboard with DAX measures
AI-powered natural language querying with LangChain
Automated CI/CD testing with GitHub Actions


👨‍💻 Author
Built by Krithesh — MSc Data and Computational Science, University College Dublin.

