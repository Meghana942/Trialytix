from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import joblib

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# -------- LOAD ML MODEL --------
model = joblib.load("model.joblib")

# -------- DATABASE --------
def init_db():
    conn = sqlite3.connect("trialytix.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drug_name TEXT,
        disease TEXT,
        phase TEXT,
        enrollment INTEGER,
        start_year INTEGER,
        base_prob REAL,
        adjusted_prob REAL,
        risk_level TEXT,
        complexity REAL,
        benchmark REAL,
        recommendation TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------- HOME --------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------- PREDICT --------
@app.post("/predict", response_class=HTMLResponse)
def predict(
    request: Request,
    drug_name: str = Form(...),
    disease: str = Form(...),
    enrollment: int = Form(...),
    start_year: int = Form(...),
    phase: str = Form(...)
):

    # -------- ML PREDICTION --------
    prob = model.predict_proba([[enrollment, start_year]])[0][1]
    base_prob = round(prob * 100, 2)

    # -------- DISEASE ADJUSTMENT --------
    disease_modifier = {
        "Breast Cancer": -5,
        "Lung Cancer": -6,
        "Type 2 Diabetes": +8,
        "Alzheimer’s": -8
    }

    adjusted_prob = round(base_prob + disease_modifier.get(disease, 0), 2)

    # -------- RISK & RECOMMENDATION --------
    if adjusted_prob > 75:
        risk_level = "Low Risk"
        recommendation = "Proceed with expansion strategy."
    elif adjusted_prob > 55:
        risk_level = "Moderate Risk"
        recommendation = "Proceed with monitoring."
    else:
        risk_level = "High Risk"
        recommendation = "Reassess trial design and optimize enrollment."

    # -------- ADDITIONAL METRICS (optional logic) --------
    complexity = round((enrollment / 50) + 40, 1)
    benchmark = round(base_prob * 0.8, 1)

    # -------- SAVE HISTORY --------
    conn = sqlite3.connect("trialytix.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO trials 
    (drug_name, disease, phase, enrollment, start_year, base_prob, adjusted_prob, risk_level, complexity, benchmark, recommendation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        drug_name,
        disease,
        phase,
        enrollment,
        start_year,
        base_prob,
        adjusted_prob,
        risk_level,
        complexity,
        benchmark,
        recommendation
    ))

    conn.commit()
    conn.close()

    return templates.TemplateResponse("result.html", {
        "request": request,
        "drug_name": drug_name,
        "disease": disease,
        "phase": phase,
        "enrollment": enrollment,
        "base_prob": base_prob,
        "adjusted_prob": adjusted_prob,
        "risk_level": risk_level,
        "complexity": complexity,
        "benchmark": benchmark,
        "recommendation": recommendation
    })


# -------- HISTORY PAGE --------
@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    conn = sqlite3.connect("trialytix.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trials ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse("history.html", {
        "request": request,
        "rows": rows
    })