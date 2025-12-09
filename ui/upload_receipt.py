import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"  

def upload_receipt_page():
    st.title("Upload Receipt & OCR Extraction")

    file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

    if file:
        st.image(file, caption="Uploaded Receipt", width=500)

        if st.button("Extract & Save Automatically"):
            files = {"file": file.getvalue()}

            # Call backend OCR endpoint
            res = requests.post(f"{API_URL}/ocr-receipt", files=files)

            if res.status_code == 200:
                data = res.json()

                st.success("Receipt processed and stored in database!")

                st.subheader("🧾 Extracted Information")
                st.write(f"**Amount:** {data.get('amount')}")
                st.write(f"**Date:** {data.get('date')}")
                st.write(f"**Category:** {data.get('category')}")
                st.write(f"**Database ID:** {data.get('id')}")

                st.text_area("Raw OCR Text", data.get("raw_text"), height=200)

            else:
                st.error("Error processing receipt. Check backend logs.")