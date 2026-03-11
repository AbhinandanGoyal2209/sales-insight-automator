import os
import io
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import requests
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "no-reply@example.com")


app = FastAPI(
    title="Sales Insight Automator API",
    description="Upload sales CSV and receive AI generated executive summary",
    version="1.0.0",
)


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Gemini AI Function
# -------------------------------
def call_gemini_with_sales_data(df: pd.DataFrame) -> str:

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    preview_rows = min(len(df), 100)
    csv_preview = df.head(preview_rows).to_csv(index=False)

    prompt = f"""
You are an expert sales analyst.

Analyze the following sales dataset and generate a professional executive summary.

Include:

• Overall performance
• Revenue trends
• Best performing region
• Product category insights
• Risks or anomalies
• 3-5 actionable recommendations

Dataset Preview:

{csv_preview}
"""

    # Use the GA v1 endpoint so models like "gemini-1.5-flash-latest"
    # work correctly.
    url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json"
    }

    params = {
        "key": GEMINI_API_KEY
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, params=params, json=body)

    if response.status_code != 200:
        raise RuntimeError(f"Gemini API error: {response.text}")

    data = response.json()

    try:
        summary = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise RuntimeError(f"Unexpected Gemini response: {data}")

    return summary.strip()


# -------------------------------
# Email Sender
# -------------------------------
def send_summary_email(to_email: str, summary: str):

    if not SMTP_HOST:
        raise RuntimeError("SMTP not configured")

    msg = MIMEText(summary)

    msg["Subject"] = "Executive Sales Summary"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:

        server.starttls()

        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)

        server.send_message(msg)


# -------------------------------
# Upload Endpoint
# -------------------------------
@app.post("/upload", summary="Upload CSV and generate AI summary")
async def upload_sales_csv(
        file: UploadFile = File(...),
        email: str = Form(...)
):

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing failed: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    try:
        summary = call_gemini_with_sales_data(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {e}")

    try:
        send_summary_email(email, summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

    return JSONResponse(
        {
            "message": "Summary generated and sent successfully",
            "email": email
        }
    )


# -------------------------------
# Health Check
# -------------------------------
@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok", "message": "Sales Insight Automator API"}