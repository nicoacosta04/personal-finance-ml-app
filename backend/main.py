from fastapi import FastAPI
from database import engine, Base
import models
from routers import transactions, ml, analytics
from routers import ocr


app = FastAPI(title="Personal Finance ML API")

Base.metadata.create_all(bind=engine)

app.include_router(transactions.router)
app.include_router(ml.router)
app.include_router(analytics.router)
app.include_router(ocr.router)

