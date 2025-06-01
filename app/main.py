from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from app.kpi import extract_kpis
from app.report import generate_report
app = FastAPI()
@app.get("/")
def welcome():
    return {"message": "Welcome to the Fintech Analyzer!"}
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        kpis = extract_kpis(contents, file.filename)
        report_path = generate_report(kpis)
        return {"message": "Report generated", "report_file": report_path}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

