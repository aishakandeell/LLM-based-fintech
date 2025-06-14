import os
#from openai import OpenAI
import cohere
import os
import pandas as pd
from docx import Document
from datetime import datetime

COHERE_API_KEY = os.getenv("COHERE_API_KEY") or "fhL35SWmjImqMN8hJo7pZYYMpxGYr7uKWu4CltM7"
co = cohere.Client(COHERE_API_KEY)

def get_ai_recommendation(financial_summary: str) -> str:
    try:
        response = co.chat(
            model="command-nightly",  # Works with .chat()
            message=f"A company has reported the following KPIs: {financial_summary}. Based on this data, give a brief strategic recommendation to improve financial performance.",
            temperature=0.7,
            max_tokens=300
        )
        return response.text.strip()
    except Exception as e:
        return f"[Cohere Chat API Error: {e}]"


def generate_report(df: pd.DataFrame, selected_options: list, custom_filename: str = None) -> str:
    doc = Document()
    doc.add_heading(" Fintech Strategic Report", level=1)

    if "kpi_summary" in selected_options:
        doc.add_heading(" KPI Summary", level=2)
        try:
            revenue = df.loc[0, "Revenue"]
            cogs = df.loc[0, "COGS"]
            gross_profit = df.loc[0, "Gross Profit"]
            ebitda = df.loc[0, "EBITDA"]
            net_income = df.loc[0, "Net Income"]
            doc.add_paragraph(f"Revenue: {revenue}")
            doc.add_paragraph(f"COGS: {cogs}")
            doc.add_paragraph(f"Gross Profit: {gross_profit}")
            doc.add_paragraph(f"EBITDA: {ebitda}")
            doc.add_paragraph(f"Net Income: {net_income}")
        except Exception as e:
            doc.add_paragraph(f"[Error extracting KPI Summary: {e}]")

    if "liquidity" in selected_options:
        doc.add_heading(" Liquidity & Solvency Metrics", level=2)
        try:
            cash = df.loc[0, "Cash"] if "Cash" in df.columns else "None"
            current_ratio = df.loc[0, "Current Ratio"] if "Current Ratio" in df.columns else "None"
            debt_ratio = df.loc[0, "Debt Ratio"] if "Debt Ratio" in df.columns else "None"
            doc.add_paragraph(f"Cash: {cash}")
            doc.add_paragraph(f"Current Ratio: {current_ratio}")
            doc.add_paragraph(f"Debt Ratio: {debt_ratio}")
        except Exception as e:
            doc.add_paragraph(f"[Error extracting Liquidity Metrics: {e}]")

    if "profitability" in selected_options:
        doc.add_heading(" Profitability Metrics", level=2)
        try:
            gross_margin = df.loc[0, "Gross Margin"] if "Gross Margin" in df.columns else "N/A"
            ebitda_margin = df.loc[0, "EBITDA Margin"] if "EBITDA Margin" in df.columns else "N/A"
            net_margin = df.loc[0, "Net Margin"] if "Net Margin" in df.columns else "N/A"
            doc.add_paragraph(f"Gross Margin: {gross_margin}")
            doc.add_paragraph(f"EBITDA Margin: {ebitda_margin}")
            doc.add_paragraph(f"Net Margin: {net_margin}")
        except Exception as e:
            doc.add_paragraph(f"[Error extracting Profitability Metrics: {e}]")

    if "ai_recommendations" in selected_options:
        doc.add_heading("🤖 AI Strategic Recommendation", level=2)
        try:
            revenue = df.loc[0, "Revenue"] if "Revenue" in df.columns else "N/A"
            net_income = df.loc[0, "Net Income"] if "Net Income" in df.columns else "N/A"
            ebitda = df.loc[0, "EBITDA"] if "EBITDA" in df.columns else "N/A"
            summary = f"Revenue: {revenue}, Net Income: {net_income}, EBITDA: {ebitda}"
            ai_suggestion = get_ai_recommendation(summary)
            doc.add_paragraph(ai_suggestion)
        except Exception as e:
            doc.add_paragraph(f"[AI Recommendation Error: {e}]")

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    if custom_filename:
        filename = f"{custom_filename}.docx"
    else:
        filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

    output_path = os.path.join(output_dir, filename)
    doc.save(output_path)
    return output_path
