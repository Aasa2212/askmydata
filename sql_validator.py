import sqlglot
from sqlglot import exp

ALLOWED_TABLES = {"sales"}
BLOCKED_KEYWORDS = {"insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke"}

def validate_sql(sql_query):
    lowered = sql_query.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in lowered:
            return False, f"Blocked keyword detected: {keyword}"

    try:
        parsed = sqlglot.parse_one(sql_query, dialect="postgres")
    except Exception as e:
        return False, f"SQL parsing failed: {e}"

    if not isinstance(parsed, exp.Select):
        return False, "Only SELECT statements are allowed"

    tables_used = {table.name.lower() for table in parsed.find_all(exp.Table)}
    unknown_tables = tables_used - ALLOWED_TABLES
    if unknown_tables:
        return False, f"Query references unknown or disallowed tables: {unknown_tables}"

    return True, "Query is valid"

if __name__ == "__main__":
    test_query = "SELECT product_name, SUM(revenue) AS total_revenue FROM sales GROUP BY product_name ORDER BY total_revenue DESC LIMIT 5;"
    is_valid, message = validate_sql(test_query)
    print(is_valid)
    print(message)
