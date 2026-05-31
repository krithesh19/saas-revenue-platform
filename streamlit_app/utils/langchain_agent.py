import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SUGGESTED_QUESTIONS = [
    "What was our MRR growth rate over the last 6 months?",
    "Which customer segment has the highest churn rate?",
    "Show me the top 10 customers by lifetime value.",
    "What is our net revenue retention (NRR) for this year?",
    "Break down our revenue waterfall for the last quarter.",
    "How does ARR compare year-over-year?",
    "Which months had the highest expansion MRR?",
    "What percentage of churned revenue came from enterprise customers?",
    "What is our average customer LTV by acquisition cohort?",
    "Show me the churn trend over the past 12 months.",
]

def _build_snowflake_uri() -> str:
    account   = os.getenv("SNOWFLAKE_ACCOUNT",  "tejxpcq-vw92165")
    user      = os.getenv("SNOWFLAKE_USER",      "")
    password  = os.getenv("SNOWFLAKE_PASSWORD",  "")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "SAAS_WH")
    database  = os.getenv("SNOWFLAKE_DATABASE",  "SAAS_REVENUE_DB")
    schema    = os.getenv("SNOWFLAKE_SCHEMA",    "GOLD")
    role      = os.getenv("SNOWFLAKE_ROLE",      "ACCOUNTADMIN")
    return (
        f"snowflake://{user}:{password}@{account}/"
        f"{database}/{schema}"
        f"?warehouse={warehouse}&role={role}"
    )

@st.cache_resource(show_spinner="Initialising AI agent…")
def get_sql_agent():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None, "GROQ_API_KEY not set in .env"
    try:
        from langchain_community.utilities import SQLDatabase
        from langchain_community.agent_toolkits import create_sql_agent
        from langchain_groq import ChatGroq

        db = SQLDatabase.from_uri(
            _build_snowflake_uri(),
            include_tables=[
                "mrr_monthly", "arr_summary", "churn_analysis",
                "customer_ltv", "revenue_waterfall",
            ],
            sample_rows_in_table_info=3,
        )

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=api_key,
        )

        agent = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="tool-calling",
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
        )
        return agent, None
    except Exception as e:
        return None, str(e)

def run_agent_query(question: str, streaming_container=None) -> str:
    agent, error = get_sql_agent()
    if error:
        return f"⚠️ Agent not available: {error}"
    try:
        result = agent.invoke({"input": question})
        return result.get("output", "No answer returned.")
    except Exception as e:
        return f"❌ Agent error: {e}"