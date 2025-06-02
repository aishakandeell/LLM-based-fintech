from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated, List
from app.kpi import extract_kpis
from app.report import generate_report

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def welcome():
    return """
    <html>
        <head>
            <title>Fintech Analyzer</title>
            <style>
                body {
                    background-color: #1f1f1f;
                    font-family: Arial, sans-serif;
                    color: white;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    font-size: 40px;
                    color: #00bcd4;
                }
                .btn {
                    display: block;
                    width: 250px;
                    margin: 15px auto;
                    padding: 12px;
                    background: linear-gradient(to right, #4a90e2, #0074d9);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    text-decoration: none;
                    font-size: 16px;
                    font-weight: bold;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                }
                .btn:hover {
                    background: linear-gradient(to right, #0074d9, #4a90e2);
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h1>📊 Welcome to the Fintech Analyzer!</h1>
            <p>Select what insights you want to generate from your financial files.</p>
            <a href="/upload-form" class="btn">Upload Financial File</a>
            <a href="/docs" class="btn">API Explorer (Swagger)</a>
            <a href="/about" class="btn">About This Tool</a>
        </body>
    </html>
    """

@app.get("/upload-form", response_class=HTMLResponse)
def upload_form():
    return """
    <html>
        <head>
            <title>Upload Financial File</title>
            <style>
                body {
                    background-color: #121212;
                    font-family: Arial, sans-serif;
                    color: white;
                    text-align: center;
                    padding: 40px;
                }
                .form-box {
                    background-color: #1f1f1f;
                    padding: 30px;
                    border-radius: 10px;
                    display: inline-block;
                    box-shadow: 0 0 12px rgba(0,0,0,0.4);
                }
                label {
                    display: block;
                    margin: 8px 0;
                    text-align: left;
                }
                input[type="submit"], input[type="file"] {
                    margin-top: 20px;
                    padding: 10px;
                    font-size: 16px;
                }
            </style>
        </head>
        <body>
            <div class="form-box">
                <h2>Upload Financial File</h2>
                <form action="/upload/" enctype="multipart/form-data" method="post">
                    <input type="file" name="file" required><br><br>
                    
                    <label><input type="checkbox" name="options" value="kpi_summary"> Include Financial KPIs</label>
                    <label><input type="checkbox" name="options" value="liquidity"> Liquidity & Solvency Metrics</label>
                    <label><input type="checkbox" name="options" value="profitability"> Profitability Metrics</label>
                    <label><input type="checkbox" name="options" value="macro"> Macroeconomic Adjustments</label>
                    <label><input type="checkbox" name="options" value="ai_recommendations"> AI Strategic Recommendations</label>
                    <label><input type="checkbox" name="options" value="benchmarking"> Benchmarking vs. Industry</label>
                    <label><input type="checkbox" name="options" value="forecasting"> Forecasting (2025–2029)</label>
                    <label><input type="checkbox" name="options" value="forensic"> Forensic Review (Red Flags)</label>
                    <label><input type="checkbox" name="options" value="restructuring"> Restructuring Plan Suggestion</label>
                    <label><input type="checkbox" name="options" value="charts"> Include Visual KPI Summary</label>
                    
                    <input type="submit" value="Upload and Analyze">
                </form>
            </div>
        </body>
    </html>
    """

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    options: Annotated[List[str], Form()] = []
):
    contents = await file.read()
    try:
        # Placeholder for now
        print(f"Selected options: {options}")
        # Uncomment this after implementing logic:
        # kpis = extract_kpis(contents, file.filename)
        # report_path = generate_report(kpis, options)
        return {
            "message": "✅ File received. Selected features will be processed.",
            "selected_options": options
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
