
from fastapi import FastAPI, UploadFile, File, Form, Request, Path
from fastapi.responses import HTMLResponse, FileResponse
from app.kpi import extract_kpis
from app.report import generate_report
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def welcome():
    return """
    <html>
        <head><title>Fintech Analyzer</title></head>
        <body style="background:#111; color:white; font-family:sans-serif; text-align:center; padding:40px;">
            <h1>Welcome to the Fintech Analyzer</h1>
            <a href="/upload-info">Upload Financial File</a>
        </body>
    </html>
    """

@app.get("/upload-info", response_class=HTMLResponse)
def upload_page():
    return """
    <html>
        <body style="background:#111; color:white; padding:40px;">
            <form action="/upload/" method="post" enctype="multipart/form-data">
                <label>Upload File:</label><br><input type="file" name="file"><br><br>
                <input type="checkbox" name="options" value="ai_recommendations" checked> Filename<br>
                <label>Overview Report Filename:</label><br>
                <input type="text" name="overview_filename" placeholder="Overview filename"><br><br>

                <input type="text" name="filename" placeholder="Report filename"><br><br>
                <label>Company Name:</label><br>
                <input type="text" name="company_name" placeholder="Enter company name"><br><br>
                <label>Industry Name:</label><br>
                <input type="text" name="industry_name" placeholder="Enter industry name"><br><br>

                <input type="submit" value="Upload and Analyze">
            </form>
        </body>
    </html>
    """

@app.post("/upload/", response_class=HTMLResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    overview_filename: str = Form(None),
    options: list[str] = Form(...),
    filename: str = Form(None),
    company_name: str = Form(None),
    industry_name: str = Form(None)

):
    contents = await file.read()
    try:
        df = extract_kpis(contents, file.filename, options)
        report_path, overview_path = generate_report(df,company_name=company_name,industry_name=industry_name,custom_filename=filename,overview_filename=overview_filename)

        return f"""
        <html><body style='background:#111; color:white; padding:40px;'>
            <h2>Report Generated</h2>
            <a href='/download/report/{os.path.basename(report_path)}'>Download Report</a>
            <a href='/download/report/{os.path.basename(overview_path)}'>Download Summary Overview Report</a>
        </body></html>
        """
    except Exception as e:
        return HTMLResponse(f"<h2 style='color:red;'>Error: {e}</h2>", status_code=400)

@app.get("/download/report/{filename}")
def download_report(filename: str = Path(...)):
    path = f"data/{filename}"
    if os.path.exists(path):
        return FileResponse(path=path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    return HTMLResponse("<h2 style='color:red;'>Report not found.</h2>", status_code=404)
