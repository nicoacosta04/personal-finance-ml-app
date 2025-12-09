from fastapi import APIRouter
import torch
from transformers import AutoTokenizer, AutoModel
import joblib

router = APIRouter()

# Load tokenizer + model (local)
tokenizer = AutoTokenizer.from_pretrained("models/minilm_embedding_model")
model = AutoModel.from_pretrained("models/minilm_embedding_model")

# Load classifier
classifier = joblib.load("models/category_classifier_sbert.pkl")

def embed(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.numpy()

def predict_category(text: str):
    emb = embed(text)
    pred = classifier.predict(emb)[0]
    return pred

@router.post("/predict-category")
def predict_api(description: str):
    return {"category": predict_category(description)}