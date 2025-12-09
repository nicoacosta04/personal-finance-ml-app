import streamlit as st
import requests
import pandas as pd
from datetime import date

API_URL = "http://172.30.31.76:8000"   # Backend URL


def view_transactions_page():

    st.title("Stored Transactions")

    # -----------------------
    # Load Transactions
    # -----------------------
    try:
        response = requests.get(f"{API_URL}/transactions")
        if response.status_code != 200:
            st.error("Failed to load transactions.")
            return

        transactions = response.json()

    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return

    if not transactions:
        st.info("No transactions yet.")
        return

    df = pd.DataFrame(transactions)
    st.dataframe(df, use_container_width=True)

    # =========================
    # EDIT / DELETE SECTION
    # =========================

    st.subheader("Edit / Delete Transaction")

    # SAFE SELECTBOX
    tx_id = st.selectbox(
        "Select transaction ID",
        options=[t["id"] for t in transactions]
    )

    # Find selected transaction
    tx = next((t for t in transactions if t["id"] == tx_id), None)

    if not tx:
        st.error("Transaction not found.")
        return

    # -------- TYPE --------
    tx_type = st.radio(
        "Type", ["expense", "income"],
        index=0 if tx["type"] == "expense" else 1
    )

    # -------- AMOUNT --------
    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=float(tx["amount"]),
        format="%.2f"
    )

    # -------- DESCRIPTION --------
    description = st.text_input("Description", tx["description"])

    # -------- DATE --------
    tx_date = st.date_input("Date", pd.to_datetime(tx["date"]))

    # -------- PAYMENT METHOD --------
    payment_method = st.selectbox(
        "Payment Method",
        ["debit_card", "credit_card", "ocr"],
        index=["debit_card", "credit_card", "ocr"].index(tx["payment_method"])
    )

    # -------- INSTALLMENTS --------
    if payment_method == "credit_card":
        current_installments = int(tx["installments"])

        # If transaction has 0 installments, default UI to 1 to avoid Streamlit error
        initial_value = current_installments if current_installments >= 1 else 1

        installments = st.number_input(
            "Installments",
            min_value=1,
            value=initial_value,
            step=1
        )

        monthly_payment = round(amount / installments, 2)

        st.number_input("Monthly payment", value=monthly_payment, disabled=True)

    else:
        installments = 0
        monthly_payment = 0.0
        st.number_input("Monthly payment", value=0.0, disabled=True)

    # -------- SAVE BUTTON --------
    if st.button("Save changes"):
        payload = {
            "type": tx_type,
            "amount": amount,
            "description": description,
            "date": str(tx_date),
            "payment_method": payment_method,
            "installments": installments,
            "monthly_payment": monthly_payment
        }

        update_res = requests.put(f"{API_URL}/transactions/{tx_id}", json=payload)

        if update_res.status_code == 200:
            st.success("Transaction updated!")
            st.rerun()
        else:
            st.error("Error updating transaction.")

    # -------- DELETE BUTTON --------
    if st.button("Delete this transaction"):
        delete_res = requests.delete(f"{API_URL}/transactions/{tx_id}")
        if delete_res.status_code == 200:
            st.success("Deleted successfully!")
            st.rerun()
        else:
            st.error("Error deleting transaction.")