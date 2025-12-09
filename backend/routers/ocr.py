from fastapi import APIRouter, UploadFile, File
import easyocr
import numpy as np
from PIL import Image
import io
import re
from routers.ml import predict_category

router = APIRouter()

# Load OCR model once
ocr_reader = easyocr.Reader(['en', 'es'], gpu=False)


@router.post("/ocr-receipt")
async def ocr_receipt(file: UploadFile = File(...)):
    # Read image bytes
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    # OCR extraction
    results = ocr_reader.readtext(image_np, detail=0)
    text = " ".join(results)

    # Extract amount
    amount_match = re.search(r"(\d+[.,]\d+)", text)
    amount = amount_match.group(1) if amount_match else None

    # Extract date
    date_match = re.search(r"(\d{4}[/-]\d{2}[/-]\d{2})", text)
    date = date_match.group(1) if date_match else None

    # Predict category using SBERT
    category = predict_category(text) if text else None

    return {
        "raw_text": text,
        "amount": amount,
        "date": date,
        "predicted_category": category,
    }