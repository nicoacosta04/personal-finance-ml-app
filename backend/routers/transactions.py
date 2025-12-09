from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
from routers.ml import predict_category
from datetime import datetime
import pytesseract
from PIL import Image
from io import BytesIO
import re

router = APIRouter()

# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------
# CREATE TRANSACTION
# ------------------------------
@router.post("/add-transaction", response_model=schemas.TransactionResponse)
def add_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db)):

    # If income → category is always Income
    if tx.type == "income":
        predicted_category = "Income"
    else:
        predicted_category = predict_category(tx.description)

    new_tx = models.Transaction(
        date=tx.date,
        amount=tx.amount,
        description=tx.description,
        payment_method=tx.payment_method,
        installments=tx.installments,
        monthly_payment=tx.monthly_payment,
        category=predicted_category,
        type=tx.type
    )

    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

# ------------------------------
# UPDATE TRANSACTION
# ------------------------------
@router.put("/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(transaction_id: int, tx_update: schemas.TransactionUpdate, db: Session = Depends(get_db)):

    tx_db = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not tx_db:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = tx_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tx_db, field, value)

    # recalculate category
    if tx_db.type == "income":
        tx_db.category = "Income"
    else:
        tx_db.category = predict_category(tx_db.description)

    db.commit()
    db.refresh(tx_db)
    return tx_db

# ------------------------------
# DELETE TRANSACTION
# ------------------------------
@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx_db = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not tx_db:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(tx_db)
    db.commit()
    return {"detail": "Transaction deleted"}

# ------------------------------
# GET TRANSACTIONS
# ------------------------------
@router.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()

# ------------------------------
# OCR RECEIPT ENDPOINT
# ------------------------------
@router.post("/ocr-receipt")
def ocr_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Read image
    image_bytes = file.file.read()
    image = Image.open(BytesIO(image_bytes))

    # OCR text extraction
    text = pytesseract.image_to_string(image)

    # ---- Extract amount ----
    amount_match = re.search(r"(\d+[.,]\d{1,2})", text)
    amount = float(amount_match.group(1).replace(",", ".")) if amount_match else None

    # ---- Extract date ----
    date_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    date = date_match.group(0) if date_match else datetime.now().strftime("%Y-%m-%d")

    # ---- Simple description ----
    description = text.split("\n")[0][:40]  # first line cleaned

    # ---- Predict category using SBERT ----
    category = predict_category(text)
    tx_type = "income" if category.lower() == "income" else "expense"

    # ===== SAVE TO DATABASE =====
    new_tx = models.Transaction(
        date=date,
        amount=amount,
        description=description,
        payment_method="ocr",
        installments=0,
        monthly_payment=0,
        category=category,
        type=tx_type
    )

    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    # Return summary
    return {
        "saved": True,
        "id": new_tx.id,
        "amount": amount,
        "date": date,
        "category": category,
        "description": description,
        "raw_text": text
    }
