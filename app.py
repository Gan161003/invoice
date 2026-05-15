import streamlit as st
import pandas as pd
from io import BytesIO

from invoice_processing import (
    extract_text_from_pdf,
    extract_text_from_image,
    extract_invoice_data
)

from PIL import Image

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Invoice Extraction App",
    layout="wide"
)

st.title("📄 Invoice Data Extraction")

st.write("Upload one or multiple invoices.")

# =========================================
# FILE UPLOAD
# =========================================

uploaded_files = st.file_uploader(
    "Upload Invoices",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# =========================================
# PROCESS
# =========================================

if uploaded_files:

    all_data = []

    progress = st.progress(0)

    for index, file in enumerate(uploaded_files):

        st.write(f"Processing: {file.name}")

        text = ""

        # PDF
        if file.type == "application/pdf":
            text = extract_text_from_pdf(file)

        # IMAGE
        else:
            image = Image.open(file)
            text = extract_text_from_image(image)

        # Extract fields
        data = extract_invoice_data(text)

        data["File Name"] = file.name

        all_data.append(data)

        progress.progress((index + 1) / len(uploaded_files))

    # =========================================
    # DATAFRAME
    # =========================================

    df = pd.DataFrame(all_data)

    st.success("Invoices Processed Successfully")

    st.dataframe(df)

    # =========================================
    # EXCEL DOWNLOAD
    # =========================================

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Invoices")

    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="invoice_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
