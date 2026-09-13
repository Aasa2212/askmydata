# AskMyData

An AI agent that turns plain English questions into validated SQL, runs them safely against a live PostgreSQL database, and returns charts and plain English explanations. Built by Aasa Singh.

## What it does

Ask a question like "what were the top 5 products by revenue" and the agent writes the actual SQL query, checks it is safe to run, executes it against PostgreSQL, generates a chart from the result, and explains the finding in plain English. Ask a follow up like "now break that down by category instead" and it understands the context from the previous question without needing it repeated.

## How it works

1. The schema is read directly from PostgreSQL, so the agent always knows the real table and column names instead of guessing.
2. The user's question, along with the schema and recent conversation history, is sent to Gemini to generate a SQL query.
3. The generated SQL is validated before execution. Only SELECT statements are allowed, and only against known tables. No INSERT, UPDATE, DELETE, DROP, or other destructive commands can ever run.
4. If the query fails when executed, the actual database error is sent back to Gemini, which corrects the query and retries, up to two times.
5. The result is turned into a chart automatically based on its shape.
6. A second call to Gemini explains the result in plain English.
7. Every question, the SQL that ran, and its outcome are logged to a query_logs table for a full audit trail.

## Features

- Schema aware SQL generation
- SQL validation and safety whitelist
- Self correcting retry loop on query failure
- Automatic chart generation
- Natural language explanations
- Multi turn follow up questions
- Query logging and audit trail
- Streamlit web interface

## Tech stack

Python, PostgreSQL, SQLAlchemy, Gemini API, sqlglot, pandas, matplotlib, Streamlit

## Running it locally

Clone the repo and install dependencies.

```
pip install -r requirements.txt
```

Create a `.env` file in the project root with your own credentials.

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
GEMINI_API_KEY=your_gemini_api_key
```

Run the web app.

```
streamlit run app.py
```

Or run the command line version.

```
python main.py
```

## Project structure

- `app.py` - Streamlit web interface
- `main.py` - command line version of the pipeline
- `schema_extractor.py` - reads the live database schema
- `sql_generator.py` - generates and corrects SQL using Gemini
- `sql_validator.py` - validates generated SQL before execution
- `chart_generator.py` - creates charts from query results
