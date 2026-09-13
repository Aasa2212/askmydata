import streamlit as st
import pandas as pd
from sqlalchemy import text
from google import genai
import os
from dotenv import load_dotenv
from schema_extractor import get_engine
from sql_generator import generate_sql, correct_sql
from sql_validator import validate_sql
from chart_generator import generate_chart

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

MAX_RETRIES = 2

st.set_page_config(page_title="AI Data Analyst", layout="centered")
st.title("AskMyData")
st.caption("Built by Aasa Singh - an AI agent that turns plain-English questions into validated SQL, runs them on PostgreSQL, and returns charts and explanations, with self-correction and multi-turn follow-ups.")

if "history" not in st.session_state:
    st.session_state.history = []

def explain_result(user_question, result_df):
    result_text = result_df.to_string(index=False)
    prompt = f"""The user asked: "{user_question}"

The query result is:
{result_text}

Write a short, plain-English explanation of this result in 1-2 sentences, as if you were a data analyst reporting a finding."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text.strip()

def execute_sql(sql):
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

def log_query(user_question, generated_sql, status, error_message=None):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO query_logs (user_question, generated_sql, status, error_message)
                VALUES (:q, :s, :st, :e)
            """),
            {"q": user_question, "s": generated_sql, "st": status, "e": error_message}
        )
        conn.commit()

question = st.text_input("Ask a question about your sales data")

if st.button("Run") and question:
    with st.spinner("Generating SQL..."):
        sql = generate_sql(question, history=st.session_state.history)

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    attempts = 0
    result_df = None
    valid = True

    while attempts <= MAX_RETRIES:
        is_valid, message = validate_sql(sql)
        if not is_valid:
            st.error(f"Validation failed: {message}")
            log_query(question, sql, "validation_failed", message)
            valid = False
            break

        try:
            result_df = execute_sql(sql)
            break
        except Exception as e:
            attempts += 1
            if attempts > MAX_RETRIES:
                st.error(f"Max retries reached: {e}")
                log_query(question, sql, "failed", str(e))
                valid = False
                break
            with st.spinner(f"Fixing query (attempt {attempts})..."):
                sql = correct_sql(question, sql, str(e))
                st.code(sql, language="sql")

    if valid and result_df is not None:
        st.subheader("Result")
        st.dataframe(result_df)

        chart_path = generate_chart(result_df, question)
        if chart_path:
            st.subheader("Chart")
            st.image(chart_path)

        with st.spinner("Generating explanation..."):
            explanation = explain_result(question, result_df)

        st.subheader("Explanation")
        st.write(explanation)

        log_query(question, sql, "success")
        st.session_state.history.append({"question": question, "sql": sql})
