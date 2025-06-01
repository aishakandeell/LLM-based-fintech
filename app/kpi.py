import pandas as pd
from io import BytesIO

def extract_kpis(file_data, filename):
    # Convert uploaded file into a DataFrame
    if filename.endswith(".xlsx"):
        df = pd.read_excel(BytesIO(file_data))
    elif filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(file_data))
    else:
        raise ValueError("Unsupported file type. Please upload .csv or .xlsx")

    # Ensure required columns exist
    required_columns = ["Revenue", "COGS"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    # Calculate KPIs
    revenue = df["Revenue"].sum()
    cogs = df["COGS"].sum()
    gross_profit = revenue - cogs
    gross_margin = (gross_profit / revenue) if revenue != 0 else 0

    return {
        "Revenue": revenue,
        "COGS": cogs,
        "Gross Profit": gross_profit,
        "Gross Margin": round(gross_margin, 2)
    }
