import streamlit as st
import requests
from datetime import date

API_URL = "http://172.30.31.76:8000"   # Backend URL

def add_transaction_page():

    st.title("➕ Add Transaction")

    # -----------------------------
    # Transaction type selector
    # -----------------------------
    transaction_type = st.radio("Transaction Type", ["expense", "income"])

    # -----------------------------
    # Shared fields
    # -----------------------------
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    description = st.text_input("Description")
    txn_date = st.date_input("Date", value=date.today())

    # -----------------------------
    # EXPENSE ONLY → Show payment info
    # -----------------------------
    installments = 0
    monthly_payment = 0.0

    if transaction_type == "expense":

        payment_method = st.selectbox("Payment Method", ["debit_card", "credit_card"])

        # If credit card → show installments
        if payment_method == "credit_card":
            installments = st.number_input("Installments", min_value=1, max_value=36, step=1)
            monthly_payment = round(amount / installments, 2)
            st.info(f"Monthly payment: **${monthly_payment}**")
        else:
            installments = 0
            monthly_payment = 0.0

    else:
        # INCOME → hidden, but included safely for backend
        payment_method = "income"       # Something harmless; backend does not use it
        installments = 0
        monthly_payment = 0.0

    # -----------------------------
    # Save transaction
    # -----------------------------
    if st.button("Save Transaction"):

        payload = {
            "date": str(txn_date),
            "amount": float(amount),
            "description": description,
            "payment_method": payment_method,
            "installments": int(installments),
            "monthly_payment": float(monthly_payment),
            "type": transaction_type
        }

        try:
            response = requests.post(f"{API_URL}/add-transaction", json=payload)

            if response.status_code == 200:
                data = response.json()
                st.success("Transaction saved successfully! 🎉")
                st.write(f"**Predicted Category:** {data['category']}")
            else:
                st.error(f"Failed to save transaction: {response.text}")

        except Exception as e:
            st.error(f"Error connecting to backend: {e}")