import pandas as pd
import io

def extract_kpis(contents: bytes, filename: str, options: list[str]) -> dict:
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(contents))
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")
    else:
        raise ValueError("Unsupported file format")

    latest = df.iloc[-1]
    result = {}

    if "kpi_summary" in options or "kpi" in options:
        result.update({
            "Revenue": latest.get("Total Revenues"),
            "COGS": latest.get("COGS"),
            "Gross Profit": latest.get("Gross Profit"),
            "EBITDA": latest.get("EBITDA"),
            "Net Income": latest.get("Net Income (NI)")
        })

    if "liquidity" in options:
        result.update({
            "Cash": latest.get("Cash"),
            "Current Ratio": latest.get("Current Ratio"),
            "Debt Ratio": latest.get("Debt Ratio")
        })

    if "profitability" in options:
        result.update({
            "Gross Margin": latest.get("Gross Margin"),
            "Net Margin": latest.get("Net Margin"),
            "EBITDA Margin": latest.get("EBITDA Margin")
        })

    if "macro" in options:
        result["Inflation Impact"] = "Adjusted using CPI index (placeholder)"
        result["FX Rate"] = "1 USD = 30.5 EGP (example)"

    if "ai_recommendations" in options:
        result["AI Recommendation"] = latest.get("Simulated Recommendation", "Restructure")

    if "benchmarking" in options:
        result["Benchmark Comparison"] = "Sector average Net Margin is 8%. Company is below."

    if "forecasting" in options:
        result["Forecast (Net Income 2026)"] = 18000  # Placeholder, could use model later

    if "forensic" in options:
        result["Accounting Red Flags"] = "Sharp increase in liabilities with no asset growth."

    if "restructuring" in options:
        result["Restructuring Plan"] = "Reduce OPEX by 10% over 2 years. Divest underperforming unit."

    if "charts" in options:
        result["Chart Ready"] = True  # Used as a flag in report generation

    return result
