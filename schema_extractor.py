import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

def get_engine():
    password = quote_plus(os.getenv('DB_PASSWORD'))
    url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(url)

def get_schema_string():
    engine = get_engine()
    inspector = inspect(engine)
    schema_lines = []
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        col_defs = [f"{col['name']} {col['type']}" for col in columns]
        schema_lines.append(f"Table {table_name}: {', '.join(col_defs)}")
    return "\n".join(schema_lines)

if __name__ == "__main__":
    print(get_schema_string())