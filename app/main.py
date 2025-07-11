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
        <head>
            <title>Fintech Analyzer</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #111;
                    color: #fff;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    color: #00d9ff;
                }
                .btn {
                    display: block;
                    width: 250px;
                    margin: 15px auto;
                    padding: 12px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    text-decoration: none;
                }
                .btn:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1> Welcome to the Fintech Analyzer!</h1>
            <a href="/upload-info" class="btn">Upload Financial File</a>
            <a href="/about" class="btn">About This Tool</a>
        </body>
    </html>
    """

@app.get("/upload-info", response_class=HTMLResponse)
def upload_page():
    return """
    <html>
        <head>
            <title>Upload Financial File</title>
            <style>
                body {
                    background-color: #111;
                    color: #fff;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .container {
                    background-color: #222;
                    padding: 30px;
                    border-radius: 10px;
                }
                label, p {
                    font-size: 16px;
                }
                input[type="submit"] {
                    margin-top: 20px;
                    background-color: white;
                    color: black;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                }
                .checkbox {
                    margin: 5px 0;
                }
                input[type="text"] {
                    width: 100%;
                    padding: 8px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Upload Financial File</h2>
                <form action="/upload/" method="post" enctype="multipart/form-data">
                    <input type="file" name="file"><br><br>
                    <div class="checkbox"><input type="checkbox" name="options" value="kpi_summary"> Include Financial KPIs</div>
                    <div class="checkbox"><input type="checkbox" name="options" value="liquidity"> Liquidity & Solvency Metrics</div>
                    <div class="checkbox"><input type="checkbox" name="options" value="profitability"> Profitability Metrics</div>
                    <div class="checkbox"><input type="checkbox" name="options" value="ai_recommendations"> AI Strategic Recommendations</div>
                    <div class="checkbox"><input type="checkbox" name="options" value="risk_restructure"> Risk Flags & Restructuring</div>

                    
                    <label for="filename">Filename:</label><br>
                    <input type="text" name="filename" placeholder="e.g., Report"><br><br>
                    
                    <input type="submit" value="Upload and Analyze">
                </form>
            </div>
        </body>
    </html>
    """


@app.post("/upload/", response_class=HTMLResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    options: list[str] = Form(...),
    filename: str = Form(None)
):

    contents = await file.read()
    try:
        kpis = extract_kpis(contents, file.filename, options)

        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame([kpis])

        # Generate report with timestamped name
        report_path = generate_report(df, options, custom_filename=filename if filename else None)

        from pathlib import Path
        filename = Path(report_path).name

        selected = "".join(f"<li>{opt.replace('_', ' ').title()}</li>" for opt in options)
        return f"""
        <html>
            <head>
                <title>Report Generated</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #111;
                        color: #eee;
                        padding: 40px;
                        text-align: center;
                    }}
                    .container {{
                        background-color: #222;
                        padding: 30px;
                        border-radius: 10px;
                        display: inline-block;
                        margin-top: 50px;
                    }}
                    .btn {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 20px;
                        display: inline-block;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2> Report Successfully Generated!</h2>
                    <p><strong>Selected Features:</strong></p>
                    <ul style="text-align: left; display: inline-block;">{selected}</ul>
                    <a class="btn" href="/download/report/{filename}" download> Download Report</a>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        return HTMLResponse(f"<h2 style='color:red;'>Error: {str(e)}</h2>", status_code=400)


@app.get("/download/report/{filename}")
def download_report(filename: str = Path(...)):
    file_path = f"data/{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    return HTMLResponse("<h2 style='color:red;'>Report not found.</h2>", status_code=404)

@app.get("/about", response_class=HTMLResponse)
def about_tool():
    return """
    <html>
        <head><title>About the Fintech Analyzer</title></head>
        <body style="background-color:#111; color:#eee; font-family:Arial; padding:40px; text-align:center;">
            <h1 style="color:#00d9ff;">Fintech Analyzer Tool Features</h1>
            
        </body>
    </html>
    """

