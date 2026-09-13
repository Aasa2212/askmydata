import os
from google import genai
from dotenv import load_dotenv
from schema_extractor import get_schema_string

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def clean_sql(raw_text):
    sql = raw_text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def build_history_context(history):
    if not history:
        return ""
    lines = []
    for turn in history[-3:]:
        lines.append(f"Previous question: {turn['question']}")
        lines.append(f"Previous SQL: {turn['sql']}")
    return "\n".join(lines)

def generate_sql(user_question, history=None):
    schema = get_schema_string()
    history_context = build_history_context(history)

    prompt = f"""You are a PostgreSQL expert. Given the database schema below, write a single valid PostgreSQL SELECT query that answers the user's question.

Schema:
{schema}

{f"Conversation history (for context on follow-up questions):{chr(10)}{history_context}" if history_context else ""}

Rules:
- Only output the raw SQL query, nothing else.
- Do not use markdown formatting or code fences.
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
- Use exact table and column names from the schema.
- If the user's question is a follow-up (e.g. "break that down further", "now by month", "what about last year"), use the conversation history to understand what "that" refers to.

User question: {user_question}

SQL query:"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return clean_sql(response.text)

def correct_sql(user_question, failed_sql, error_message):
    schema = get_schema_string()
    prompt = f"""You are a PostgreSQL expert. The following SQL query failed when run against the database.

Schema:
{schema}

Original question: {user_question}

Failed SQL:
{failed_sql}

Error message:
{error_message}

Fix the SQL query so it runs correctly against the schema above. Only output the corrected raw SQL query, nothing else. Do not use markdown formatting or code fences. Only generate SELECT statements."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return clean_sql(response.text)

if __name__ == "__main__":
    question = input("Ask a question about your sales data: ")
    sql = generate_sql(question)
    print(sql)
