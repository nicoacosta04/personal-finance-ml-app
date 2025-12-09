from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    amount = Column(Float)
    description = Column(String)
    category = Column(String)
    type = Column(String)
    payment_method = Column(String)
    installments = Column(Integer)
    monthly_payment = Column(Float)