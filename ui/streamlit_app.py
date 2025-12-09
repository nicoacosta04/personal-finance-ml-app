import streamlit as st
import home
import add_transaction
import view_transactions
import analytics
from upload_receipt import upload_receipt_page


st.set_page_config(page_title="Personal Finance ML App", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio(
    "Go to",
    ["Home", "Add Transaction", "View Transactions", "Analytics Dashboard", "Upload Receipt"]
)


# Page Rendering
if choice == "Home":
    home.home_page()

elif choice == "Add Transaction":
    add_transaction.add_transaction_page()

elif choice == "View Transactions":
    view_transactions.view_transactions_page()

elif choice == "Analytics Dashboard":
    analytics.analytics_page()

elif choice == "Upload Receipt":
    upload_receipt_page()

