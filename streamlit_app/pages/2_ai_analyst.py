"""
streamlit_app/pages/2_ai_analyst.py
💬 AI Revenue Analyst — Natural language Q&A powered by LangChain + GPT-4o
"""

import streamlit as st
from utils.langchain_agent import run_agent_query, SUGGESTED_QUESTIONS, get_sql_agent
from utils.snowflake_connector import test_connection
import time

st.set_page_config(page_title="AI Revenue Analyst", page_icon="💬", layout="wide")

st.title("💬 AI Revenue Analyst")
st.markdown(
    "Ask any question about your SaaS revenue data in plain English. "
    "The AI agent writes the SQL, runs it against your Snowflake GOLD schema, "
    "and explains the results."
)

col_status1, col_status2 = st.columns([1, 4])
with col_status1:
    if test_connection():
        st.success("✅ Snowflake connected")
    else:
        st.error("❌ Snowflake offline")

with col_status2:
    agent, agent_error = get_sql_agent()
    if agent:
        st.success("✅ AI Agent ready (GPT-4o)")
    else:
        st.warning(f"⚠️ AI Agent: {agent_error or 'Not initialised'}")

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 Hello! I'm your AI Revenue Analyst. I have full access to your "
                "Snowflake GOLD schema (`mrr_monthly`, `arr_summary`, `churn_analysis`, "
                "`customer_ltv`, `revenue_waterfall`).\n\n"
                "Ask me anything about your SaaS revenue — I'll write the SQL and "
                "explain the results in plain English."
            ),
        }
    ]

with st.expander("💡 Suggested questions — click to use", expanded=True):
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"suggest_{i}", use_container_width=True):
                st.session_state["prefill_question"] = q

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prefill = st.session_state.pop("prefill_question", "")
user_input = st.chat_input(
    "Ask about your revenue data…",
    key="chat_input",
) or prefill

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("🤔 Thinking…")
        stream_container = st.container()
        start = time.time()
        answer = run_agent_query(user_input, streaming_container=stream_container)
        elapsed = time.time() - start
        thinking_placeholder.empty()
        st.markdown(answer)
        st.caption(f"⏱ {elapsed:.1f}s · Snowflake GOLD · GPT-4o")

    st.session_state.messages.append({"role": "assistant", "content": answer})

st.markdown("---")
if st.button("🗑️ Clear conversation", type="secondary"):
    st.session_state.messages = []
    st.rerun()