import os
#from openai import OpenAI
import cohere
import os
import pandas as pd
from docx import Document
from datetime import datetime
from docx.enum.text import WD_ALIGN_PARAGRAPH
import matplotlib.pyplot as plt

COHERE_API_KEY = os.getenv("COHERE_API_KEY") or "fhL35SWmjImqMN8hJo7pZYYMpxGYr7uKWu4CltM7"
co = cohere.Client(COHERE_API_KEY)
def safe_float(val):
    try:
        return float(val)
    except:
        return None


def get_value(df_or_row, *possible_columns):
    for col in possible_columns:
        if isinstance(df_or_row, pd.Series):  # a single row
            if col in df_or_row:
                return df_or_row[col]
        elif isinstance(df_or_row, pd.DataFrame):  # whole table
            if col in df_or_row.columns:
                return df_or_row.loc[0, col]
    return "N/A"


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

def generate_risk_flags(df):
    flags = []
    recommendations = []

    try:
        revenue = safe_float(get_value(df, "Revenue", "الإيرادات"))
        net_income = safe_float(get_value(df, "Net Income", "صافي الدخل"))
        debt_ratio = safe_float(get_value(df, "Debt Ratio", "نسبة الدين"))
        current_ratio = safe_float(get_value(df, "Current Ratio", "النسبة الجارية"))


        if revenue is not None and revenue < 0:
            flags.append("Revenue is negative — unsustainable operations.")
            recommendations.append("Review revenue streams and assess product/service pricing strategies.")
        if net_income is not None and net_income < 0:
            flags.append("Net income is negative — potential profitability issue.")
            recommendations.append("Reduce operating expenses or optimize cost structure.")
        if current_ratio is not None and current_ratio < 1:
            flags.append("Current ratio < 1 — potential liquidity risk.")
            recommendations.append("Consider short-term financing or renegotiate payable terms.")
        if debt_ratio is not None and debt_ratio > 0.7:
            flags.append("Debt ratio exceeds 70% — leverage may be too high.")
            recommendations.append("Explore debt restructuring or equity injection to rebalance capital.")

    except Exception as e:
        flags.append(f"Could not assess risk flags due to data error: {e}")
        recommendations.append("Validate uploaded financial data format for accurate analysis.")

    if not flags:
        flags.append("No immediate red flags detected. Keep monitoring.")
        recommendations.append("Continue periodic monitoring and maintain healthy financial ratios.")

    return flags, recommendations

def add_trend_chart(doc, df, metric_name):
    try:
        if metric_name not in df.columns:
            doc.add_paragraph(f"{metric_name} data unavailable for trend chart.")
            return

        plt.figure(figsize=(6, 3))
        df[metric_name].plot(kind='line', marker='o', title=f"{metric_name} Trend")
        plt.ylabel(metric_name)
        plt.tight_layout()
        
        chart_path = f"data/{metric_name}_trend.png"
        plt.savefig(chart_path)
        plt.close()
        
        doc.add_picture(chart_path)
    except Exception as e:
        doc.add_paragraph(f"[Chart Error for {metric_name}: {e}]")

def generate_report(df: pd.DataFrame, selected_options: list, custom_filename: str = None) -> str:
    doc = Document()
    doc.add_heading(" Fintech Strategic Report", level=1)

    if "kpi_summary" in selected_options:
        doc.add_heading(" KPI Summary", level=2)
        try:
            revenue = get_value(df, "Revenue", "الإيرادات")
            cogs = get_value(df, "COGS", "تكلفة البضاعة")
            gross_profit = get_value(df, "Gross Profit", "الربح الإجمالي")
            ebitda = get_value(df, "EBITDA", "الأرباح قبل الفوائد")
            net_income = get_value(df, "Net Income", "صافي الدخل")

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
            cash = get_value(df, "Cash", "النقدية")
            current_ratio = get_value(df, "Current Ratio", "النسبة الجارية")
            debt_ratio = get_value(df, "Debt Ratio", "نسبة الدين")

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
            gross_margin = get_value(df, "Gross Margin", "هامش الربح الإجمالي")
            ebitda_margin = get_value(df, "EBITDA Margin", "هامش الأرباح قبل الفوائد")
            net_margin = get_value(df, "Net Margin", "هامش صافي الربح")

            ebitda_margin = df.loc[0, "EBITDA Margin"] if "EBITDA Margin" in df.columns else "N/A"
            net_margin = df.loc[0, "Net Margin"] if "Net Margin" in df.columns else "N/A"
            doc.add_paragraph(f"Gross Margin: {gross_margin}")
            doc.add_paragraph(f"EBITDA Margin: {ebitda_margin}")
            doc.add_paragraph(f"Net Margin: {net_margin}")
        except Exception as e:
            doc.add_paragraph(f"[Error extracting Profitability Metrics: {e}]")

    if "ai_recommendations" in selected_options:
        doc.add_heading("AI Strategic Recommendation", level=2)
        try:
            revenue = get_value(df, "Revenue", "الإيرادات")
            net_income = get_value(df, "Net Income", "صافي الدخل")
            ebitda = get_value(df, "EBITDA", "الأرباح قبل الفوائد")

            summary = f"Revenue: {revenue}, Net Income: {net_income}, EBITDA: {ebitda}"
            ai_suggestion = get_ai_recommendation(summary)
            doc.add_paragraph(ai_suggestion)
        except Exception as e:
            doc.add_paragraph(f"[AI Recommendation Error: {e}]")

    if "risk_restructure" in selected_options:
        doc.add_heading("Risk Flags & Restructuring Suggestions", level=2)
        doc.add_heading("Detected Risk Flags:", level=3)
        flags, recs = generate_risk_flags(df)
        for flag in flags:
            doc.add_paragraph(flag)

        doc.add_heading("Recommended Restructuring Actions:", level=3)
        for rec in recs:
            doc.add_paragraph(f"- {rec}")

    if "industry_benchmarking" in selected_options:
        add_industry_benchmarking(doc, df)
        doc.add_heading("Trend Charts", level=2)
        add_trend_chart(doc, df, "Revenue")
        add_trend_chart(doc, df, "Net Income")

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    if custom_filename:
        filename = f"{custom_filename}.docx"
    else:
        filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

    output_path = os.path.join(output_dir, filename)
    doc.save(output_path)
    return output_path
