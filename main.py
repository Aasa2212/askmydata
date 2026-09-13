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

def run_pipeline(user_question, history):
    sql = generate_sql(user_question, history=history)
    print(f"Generated SQL: {sql}")

    attempts = 0
    result_df = None

    while attempts <= MAX_RETRIES:
        is_valid, message = validate_sql(sql)
        if not is_valid:
            print(f"Validation failed: {message}")
            log_query(user_question, sql, "validation_failed", message)
            return None

        try:
            result_df = execute_sql(sql)
            break
        except Exception as e:
            attempts += 1
            print(f"Execution failed (attempt {attempts}): {e}")
            if attempts > MAX_RETRIES:
                print("Max retries reached. Giving up.")
                log_query(user_question, sql, "failed", str(e))
                return None
            sql = correct_sql(user_question, sql, str(e))
            print(f"Corrected SQL: {sql}")

    print(result_df)

    chart_path = generate_chart(result_df, user_question)
    if chart_path:
        print(f"Chart saved to: {chart_path}")

    explanation = explain_result(user_question, result_df)
    print(f"\nExplanation: {explanation}")

    log_query(user_question, sql, "success")

    history.append({"question": user_question, "sql": sql})

    return result_df

if __name__ == "__main__":
    history = []
    print("Type 'exit' to quit.")
    while True:
        question = input("\nAsk a question about your sales data: ")
        if question.strip().lower() == "exit":
            break
        run_pipeline(question, history)
