from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import shutil
import uuid
import os
from main import process_file   # import your lead-processing function

app = FastAPI()

@app.post("/process-leads")
async def process_leads(file: UploadFile = File(...)):
    # Ensure uploaded file is CSV
    if not file.filename.endswith(".csv"):
        return JSONResponse(
            {"error": "Please upload a valid CSV file"}, 
            status_code=400
        )

    # Save uploaded file to disk
    temp_input_path = f"inputs/uploaded_leads.csv"
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Output JSON file path
    output_path = f"outputs/output_enriched_leads.json"

    # Run your main() processing logic
    process_file(temp_input_path, output_path)

    # Return enriched JSON file for download
    return FileResponse(
        output_path,
        filename="output_enriched_leads.json",
        media_type="application/json"
    )
