from pydantic import BaseModel


class TransactionCreate(BaseModel):
    date: str
    amount: float
    description: str
    payment_method: str
    installments: int
    monthly_payment: float
    type: str | None = None

class TransactionUpdate(BaseModel):
    "Used for editing transactions"
    date: str | None = None
    amount: float | None = None
    description: str | None = None
    payment_method: str | None = None
    installments: int | None = None
    monthly_payment: float | None = None
    type: str | None = None


class TransactionResponse(TransactionCreate):
    id: int
    category: str
    type: str

    # Pydantic v2 config
    model_config = {
        "from_attributes": True
    }


class MonthlySummary(BaseModel):
    month: str            # "2025-05"
    total_expenses: float
    total_income: float
    net_cashflow: float