
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

            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>
                :root{
                    --bg:#0b1f3a;           /* dark blue background */
                    --text:#ffffff;         /* white text */
                    --muted:#c9d7ef;        /* soft light text */
                    --primary:#2d6cdf;      /* button blue */
                    --primary-hover:#1f58c7;
                    --card:#0e274a;
                }
                *{box-sizing:border-box;}
                body{
                    margin:0; background:var(--bg); color:var(--text);
                    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
                    min-height:100vh; display:grid; place-items:center; text-align:center;
                    padding:40px;
                }
                h1{font-size:clamp(28px,4vw,48px); margin:0 0 24px;}
                p{color:var(--muted); margin:0 0 32px;}
                .btn{
                 display:inline-block; padding:12px 20px; border-radius:10px;
                    background:var(--primary); color:#fff; text-decoration:none; font-weight:600;
                    border:none; cursor:pointer; transition:background .2s ease;
                }
                .btn:hover{ background:var(--primary-hover); }
                .card{
                    background:var(--card); padding:32px; border-radius:16px;
                    box-shadow:0 10px 30px rgba(0,0,0,.25);
                }
            </style>

        </head>
        <body>
            <div class="card">
                <h1>Welcome to the Fintech Analyzer</h1>
                <p>Upload your Excel/CSV to generate a full report and summary overview.</p>
                <a class="btn" href="/upload-info">Upload Financial File</a>
            </div>
        </body>
    </html>
    """

@app.get("/upload-info", response_class=HTMLResponse)
def upload_page():
    return """
    <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Upload • Fintech Analyzer</title>
        <style>
          :root{
            --bg:#0b1f3a;          /* page background */
            --card:#0e274a;        /* panel */
            --text:#ffffff;        /* main text */
            --muted:#c9d7ef;       /* helper text */
            --input:#112e57;       /* input background */
            --border:#284a83;      /* input border */
            --primary:#2d6cdf;     /* button */
            --primary-hover:#1f58c7;
          }
          *{box-sizing:border-box}
          body{
            margin:0; background:var(--bg); color:var(--text);
            font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial;
            padding:48px;
          }
          .wrap{max-width:760px; margin:0 auto;}
          .card{
            background:var(--card); border-radius:22px; padding:32px;
            box-shadow:0 18px 40px rgba(0,0,0,.35);
          }
          h1{margin:0 0 6px; font-size:clamp(22px,3vw,34px)}
          .sub{margin:0 0 22px; color:var(--muted)}
          label{display:block; margin:14px 0 8px; font-weight:600}
          .text{
            width:100%; padding:12px 14px; border-radius:12px;
            border:1px solid var(--border); background:var(--input); color:var(--text);
            outline:none;
          }
          .text::placeholder{color:var(--muted)}
          .btn{
            display:inline-block; padding:12px 20px; border-radius:12px;
            background:var(--primary); color:#fff; border:none; font-weight:700;
            cursor:pointer; transition:background .2s ease; margin-top:6px;
          }
          .btn:hover{background:var(--primary-hover)}
          .row{display:flex; align-items:center; gap:10px; flex-wrap:wrap}
          .hint{color:var(--muted); font-size:13px}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="card">
            <h1>Upload & Analyze</h1>
            <p class="sub">Upload your Excel/CSV and fill the details below to generate your reports.</p>

            <!-- Keep your original form + field names -->
            <form action="/upload/" method="post" enctype="multipart/form-data">
              <label for="file">Upload File:</label>
              <input id="file" type="file" name="file" />

              <div style="margin-top:10px;">
                <input id="use-filename" type="checkbox" name="options" value="ai_recommendations" checked>
                <label for="use-filename" style="display:inline; font-weight:600; margin-left:6px;">Filename</label>
              </div>

              <label for="overview">Overview Report Filename:</label>
              <input id="overview" class="text" type="text" name="overview_filename" placeholder="Overview filename">

              <label for="report">Report Filename:</label>
              <input id="report" class="text" type="text" name="filename" placeholder="Report filename">

              <label for="company">Company Name:</label>
              <input id="company" class="text" type="text" name="company_name" placeholder="Enter company name">

              <label for="industry">Industry Name:</label>
              <input id="industry" class="text" type="text" name="industry_name" placeholder="Enter industry name">

              <div style="margin-top:18px;">
                <button class="btn" type="submit">Upload and Analyze</button>
              </div>
            </form>
          </div>
        </div>
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

        # return f"""
        # <html><body style='background:#111; color:white; padding:40px;'>
        #     <h2>Report Generated</h2>
        #     <a href='/download/report/{os.path.basename(report_path)}'>Download Report</a>
        #     <a href='/download/report/{os.path.basename(overview_path)}'>Download Summary Overview Report</a>
        # </body></html>
        # """

        return f"""
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Report Generated • Fintech Analyzer</title>
                <style>
                    :root{{ --bg:#0b1f3a; --card:#0e274a; --text:#ffffff; --muted:#c9d7ef; --primary:#2d6cdf; --primary-hover:#1f58c7; }}
                    *{{box-sizing:border-box}}
                    body{{
                        margin:0; background:var(--bg); color:var(--text);
                        font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial;
                        height:100vh; display:flex; align-items:center; justify-content:center; padding:24px;
                    }}
                    .card{{
                        background:var(--card); border-radius:22px; padding:28px;
                        box-shadow:0 18px 40px rgba(0,0,0,.35); max-width:640px; width:100%; text-align:center;
                    }}
                    h2{{margin:0 0 10px; font-size:clamp(22px,3vw,34px)}}
                    p{{margin:0 0 18px; color:var(--muted)}}
                    .btn{{
                        display:inline-block; padding:12px 18px; border-radius:12px;
                        background:var(--primary); color:#fff; text-decoration:none; font-weight:700;
                        margin:8px 6px 0 6px; transition:background .2s ease;
                    }}
                    .btn:hover{{ background:var(--primary-hover); }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>Report Generated</h2>
                    <p>Your files are ready to download.</p>
                    <a class="btn" href='/download/report/{os.path.basename(report_path)}'>Download Report</a>
                    <a class="btn" href='/download/report/{os.path.basename(overview_path)}'>Download Summary Overview</a>
                </div>
            </body>
            </html>
            """    

    except Exception as e:
        return HTMLResponse(f"<h2 style='color:red;'>Error: {e}</h2>", status_code=400)

@app.get("/download/report/{filename}")
def download_report(filename: str = Path(...)):
    path = f"data/{filename}"
    if os.path.exists(path):
        return FileResponse(path=path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    return HTMLResponse("<h2 style='color:red;'>Report not found.</h2>", status_code=404)
