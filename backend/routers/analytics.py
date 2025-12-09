from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import schemas 
import pandas as pd
from datetime import datetime, date


router = APIRouter()


# ------------------------------
# DATABASE SESSION DEPENDENCY
# ------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------
# MONTHLY SUMMARY ENDPOINT
# ------------------------------
@router.get("/analytics/monthly-summary", response_model=list[schemas.MonthlySummary])
def monthly_summary(db: Session = Depends(get_db)):
    # Fetch all transactions
    txs = db.query(models.Transaction).all()

    if not txs:
        return []

    # Build DataFrame from DB entries
    df = pd.DataFrame([{
        "date": t.date,
        "amount": t.amount,
        "type": t.type
    } for t in txs])

    # Convert to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Create YYYY-MM grouping key
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Separate expenses and incomes
    expenses = df[df["type"] == "expense"].groupby("month")["amount"].sum()
    income = df[df["type"] == "income"].groupby("month")["amount"].sum()

    # Ensure consistent months
    all_months = sorted(set(expenses.index).union(set(income.index)))

    summaries = []
    for m in all_months:
        total_exp = float(expenses.get(m, 0.0))
        total_inc = float(income.get(m, 0.0))
        net = total_inc - total_exp

        summaries.append(
            schemas.MonthlySummary(
                month=m,
                total_expenses=round(total_exp, 2),
                total_income=round(total_inc, 2),
                net_cashflow=round(net, 2)
            )
        )

    return summaries

@router.get("/analytics/balance")
def balance(db: Session = Depends(get_db)):
    txs = db.query(models.Transaction).all()
    income = sum(t.amount for t in txs if t.type == "income")
    expenses = sum(t.amount for t in txs if t.type == "expense")
    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "balance": round(income - expenses, 2)
    }


@router.get("/analytics/credit-overview")
def credit_overview(db: Session = Depends(get_db)):
    txs = db.query(models.Transaction).filter(
        models.Transaction.type == "expense",
        models.Transaction.payment_method == "credit_card",
        models.Transaction.installments > 0
    ).all()

    today = date.today()
    items = []

    for t in txs:
        start_date = datetime.strptime(t.date, "%Y-%m-%d").date()
        months_elapsed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
        remaining_installments = max(0, t.installments - months_elapsed)
        remaining_debt = remaining_installments * t.monthly_payment

        items.append({
            "id": t.id,
            "description": t.description,
            "start_date": t.date,
            "amount": t.amount,
            "installments": t.installments,
            "remaining_installments": remaining_installments,
            "monthly_payment": t.monthly_payment,
            "remaining_debt": round(remaining_debt, 2)
        })

    total_monthly = sum(i["monthly_payment"] for i in items if i["remaining_installments"] > 0)
    total_remaining = sum(i["remaining_debt"] for i in items)

    return {
        "items": items,
        "total_monthly_payment": round(total_monthly, 2),
        "total_remaining_debt": round(total_remaining, 2)
    }


@router.get("/analytics/anomalies")
def anomalies(db: Session = Depends(get_db)):
    from sklearn.ensemble import IsolationForest

    txs = db.query(models.Transaction).filter(models.Transaction.type == "expense").all()
    if len(txs) < 10:
        # Not enough data to do anomaly detection
        return {"anomalies": []}

    df = pd.DataFrame([{
        "id": t.id,
        "date": t.date,
        "amount": t.amount,
        "description": t.description,
    } for t in txs])

    df["date"] = pd.to_datetime(df["date"])
    df["day_of_week"] = df["date"].dt.weekday + 1
    df["month"] = df["date"].dt.month

    features = df[["amount", "day_of_week", "month"]]

    model_if = IsolationForest(contamination=0.1, random_state=42)
    df["anomaly_score"] = model_if.fit_predict(features)

    anomalies_df = df[df["anomaly_score"] == -1].sort_values("amount", ascending=False)

    anomalies = anomalies_df[["id", "date", "amount", "description"]].to_dict(orient="records")
    return {"anomalies": anomalies}