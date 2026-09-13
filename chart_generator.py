import matplotlib.pyplot as plt
import pandas as pd

def generate_chart(df, question, output_path="chart_output.png"):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(exclude="number").columns.tolist()

    if not numeric_cols or not text_cols:
        print("Cannot auto-chart this result shape")
        return None

    x_col = text_cols[0]
    y_col = numeric_cols[0]

    plt.figure(figsize=(8, 5))
    plt.bar(df[x_col], df[y_col], color="#4C72B0")
    plt.title(question)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path

if __name__ == "__main__":
    sample = pd.DataFrame({
        "product_name": ["Product C", "Product G", "Product H", "Product D", "Product B"],
        "total_revenue": [658847.33, 604965.55, 591922.07, 564149.91, 557133.92]
    })
    path = generate_chart(sample, "Top 5 Products by Revenue")
    print(f"Chart saved to: {path}")
