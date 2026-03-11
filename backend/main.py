# import io
# import pandas as pd
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse

# app = FastAPI(
#     title="Sales Insight Automator API",
#     description="Upload sales CSV and generate executive summary",
#     version="1.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # -------------------------------
# # Sales Summary Generator
# # -------------------------------

# def generate_sales_summary(df: pd.DataFrame):

#     total_revenue = df["Revenue"].sum()
#     total_units = df["Units_Sold"].sum()

#     region_sales = df.groupby("Region")["Revenue"].sum()
#     top_region = region_sales.idxmax()

#     product_sales = df.groupby("Product_Category")["Revenue"].sum()
#     top_product = product_sales.idxmax()

#     cancelled_orders = df[df["Status"] == "Cancelled"].shape[0]

#     summary = f"""
# EXECUTIVE SALES SUMMARY

# Total Revenue: ${total_revenue}
# Total Units Sold: {total_units}

# Top Performing Region: {top_region}
# Top Product Category: {top_product}

# Cancelled Orders: {cancelled_orders}

# KEY INSIGHTS
# • Electronics appear to drive the highest revenue.
# • The {top_region} region shows the strongest sales.
# • Cancelled orders indicate potential operational issues.

# RECOMMENDATIONS
# • Increase inventory for high-performing products.
# • Focus marketing in high-revenue regions.
# • Investigate causes of order cancellations.
# """

#     return summary


# # -------------------------------
# # Upload Endpoint
# # -------------------------------

# @app.post("/upload")
# async def upload_sales_csv(
#     file: UploadFile = File(...),
#     email: str = Form(...)
# ):

#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Only CSV files allowed")

#     try:
#         contents = await file.read()
#         df = pd.read_csv(io.BytesIO(contents))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"CSV parsing failed: {e}")

#     if df.empty:
#         raise HTTPException(status_code=400, detail="CSV file is empty")

#     summary = generate_sales_summary(df)

#     return JSONResponse(
#         {
#             "message": "Summary generated successfully",
#             "email": email,
#             "summary": summary
#         }
#     )


# # -------------------------------
# # Health Check
# # -------------------------------

# @app.get("/")
# def root():
#     return {
#         "status": "ok",
#         "message": "Sales Insight Automator API"
#     }



import io
import pandas as pd
import os

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import aiosmtplib
from email.message import EmailMessage


app = FastAPI(
    title="Sales Insight Automator API",
    description="Upload sales CSV and generate executive summary",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# EMAIL SENDER
# -------------------------------

async def send_email(receiver_email: str, summary: str):

    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Sales Insight Summary"

    message.set_content(summary)

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=sender_email,
        password=sender_password,
    )


# -------------------------------
# Sales Summary Generator
# -------------------------------

def generate_sales_summary(df: pd.DataFrame):

    total_revenue = df["Revenue"].sum()
    total_units = df["Units_Sold"].sum()

    region_sales = df.groupby("Region")["Revenue"].sum()
    top_region = region_sales.idxmax()

    product_sales = df.groupby("Product_Category")["Revenue"].sum()
    top_product = product_sales.idxmax()

    cancelled_orders = df[df["Status"] == "Cancelled"].shape[0]

    summary = f"""
EXECUTIVE SALES SUMMARY

Total Revenue: ${total_revenue}
Total Units Sold: {total_units}

Top Performing Region: {top_region}
Top Product Category: {top_product}

Cancelled Orders: {cancelled_orders}

KEY INSIGHTS
• Electronics appear to drive the highest revenue.
• The {top_region} region shows the strongest sales.
• Cancelled orders indicate potential operational issues.

RECOMMENDATIONS
• Increase inventory for high-performing products.
• Focus marketing in high-revenue regions.
• Investigate causes of order cancellations.
"""

    return summary


# -------------------------------
# Upload Endpoint
# -------------------------------

@app.post("/upload")
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

    summary = generate_sales_summary(df)

    # SEND EMAIL
    try:
        await send_email(email, summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {e}")

    return JSONResponse(
        {
            "message": "Summary generated and email sent successfully",
            "email": email,
            "summary": summary
        }
    )


# -------------------------------
# Health Check
# -------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Sales Insight Automator API"
    }