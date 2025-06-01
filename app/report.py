from docx import Document
import os

def generate_report(kpis: dict):
    doc = Document()
    doc.add_heading("📄 Fintech Evaluation Report", level=1)

    # Add a section for each KPI
    for key, value in kpis.items():
        doc.add_paragraph(f"{key}: {value}")

    # Create output folder if it doesn't exist
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "financial_report.docx")
    doc.save(output_path)
    return output_path
