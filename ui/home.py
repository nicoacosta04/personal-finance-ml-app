import streamlit as st

def home_page():
    st.title("💰 Personal Finance ML App")

    st.write("Welcome to your intelligent financial dashboard!")
    st.write("This app allows you to:")
    
    st.markdown("""
    - Automatically categorize your expenses using Machine Learning  
    - Store transactions in a local database  
    - Analyze monthly spending and income trends  
    - Track credit card commitments  
    - Prepare for future anomaly detection and financial alerts  
    """)