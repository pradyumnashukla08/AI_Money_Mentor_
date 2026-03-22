import io
import pandas as pd
from datetime import datetime
import pyxirr
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

app = FastAPI(title="AI Portfolio Mentor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/calculate-xirr")
async def calculate_xirr(
    file: UploadFile = File(...),
    current_value: float = Form(...)
):
    try:
        contents = await file.read()
        
        if not file.filename.lower().endswith('.csv'):
            return JSONResponse(status_code=400, content={"success": False, "error": "Only CSV files are currently supported."})
            
        df = pd.read_csv(io.BytesIO(contents))
        
        if 'Date' not in df.columns or 'Amount' not in df.columns:
            return JSONResponse(status_code=400, content={"success": False, "error": "CSV must contain 'Date' and 'Amount' columns."})
            
        # Parse Dates
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Fix typing issues with pandas scalars
        total_invested = float(abs(df[df['Amount'] < 0]['Amount'].sum()))

        today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
        current_value_row = pd.DataFrame([{'Date': today, 'Transaction Type': 'Current Value', 'Amount': float(current_value)}])
        calc_df = pd.concat([df, current_value_row], ignore_index=True)

        xirr_rate = pyxirr.xirr(calc_df['Date'], calc_df['Amount'])
        xirr_pct = float(xirr_rate * 100) if xirr_rate is not None else None

        return {
            "success": True,
            "total_invested": total_invested,
            "current_value": float(current_value),
            "xirr": xirr_pct
        }
            
    except Exception as e:
        logging.error(f"Error processing XIRR: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
