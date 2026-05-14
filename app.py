# app.py

import streamlit as st
import pandas as pd
import re
from pdf2image import convert_from_bytes
from paddleocr import PaddleOCR
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Invoice OCR Engine",
    layout="wide"
)

st.title("📄 AI Invoice OCR Engine")

st.markdown("---")

# =========================================================
# LOAD OCR MODEL
# =========================================================

@st.cache_resource
def load_ocr():

    ocr_model = PaddleOCR(
        use_angle_cls=True,
        lang='en'
    )

    return ocr_model

ocr = load_ocr()

# =========================================================
# FIELD KEYWORDS
# =========================================================

FIELD_KEYWORDS = {

    "Invoice Number": [
        "invoice no",
        "invoice num",
        "invoice number",
        "bill no"
    ],

    "PO Number": [
        "po no",
        "po num",
        "purchase order",
        "po number"
    ],

    "Invoice Date": [
        "invoice date",
        "bill date",
        "date"
    ],

    "Taxable Amount": [
        "taxable amount",
        "subtotal",
        "net amount"
    ],

    "Total Amount": [
        "grand total",
        "invoice total",
        "total payable",
        "amount due"
    ]
}

# =========================================================
# REGEX PATTERNS
# =========================================================

PATTERNS = {

    "amount": r'[\d,]+\.\d{2}',

    "po_number": r'PO\/[\d\-\/]+',

    "invoice_number": r'[A-Z0-9\/\-]+'
}

# =========================================================
# OCR FULL PDF
# =========================================================

def extract_full_text(uploaded_file):

    pdf_bytes = uploaded_file.read()

    images = convert_from_bytes(pdf_bytes)

    all_text = []

    for image in images:

        result = ocr.ocr(image)

        for line in result[0]:

            text = line[1][0]

            all_text.append(text)

    full_text = "\n".join(all_text)

    return full_text

# =========================================================
# FIND LINE USING KEYWORDS
# =========================================================

def find_field_line(full_text, keywords):

    lines = full_text.split("\n")

    for line in lines:

        lower_line = line.lower()

        for keyword in keywords:

            if keyword in lower_line:

                return line

    return ""

# =========================================================
# PARSE VALUE
# =========================================================

def parse_value(field_name, line):

    if not line:

        return ""

    # =====================================================
    # AMOUNT
    # =====================================================

    if field_name in [
        "Taxable Amount",
        "Total Amount"
    ]:

        match = re.search(
            PATTERNS["amount"],
            line
        )

        if match:

            return match.group()

    # =====================================================
    # PO NUMBER
    # =====================================================

    if field_name == "PO Number":

        match = re.search(
            PATTERNS["po_number"],
            line,
            re.IGNORECASE
        )

        if match:

            return match.group()

    # =====================================================
    # GENERIC SPLIT
    # =====================================================

    if ":" in line:

        return line.split(":")[-1].strip()

    return line

# =========================================================
# PROCESS SINGLE PDF
# =========================================================

def process_invoice(uploaded_file):

    full_text = extract_full_text(uploaded_file)

    extracted_data = {}

    # =====================================================
    # FIELD EXTRACTION
    # =====================================================

    for field, keywords in FIELD_KEYWORDS.items():

        matched_line = find_field_line(
            full_text,
            keywords
        )

        value = parse_value(
            field,
            matched_line
        )

        extracted_data[field] = value

    extracted_data["File Name"] = uploaded_file.name

    return extracted_data, full_text

# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_files = st.file_uploader(
    "Upload Invoice PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# =========================================================
# PROCESS BUTTON
# =========================================================

if uploaded_files:

    st.success(f"{len(uploaded_files)} PDFs Uploaded")

    if st.button("🚀 Process Invoices"):

        final_data = []

        for file in uploaded_files:

            st.markdown("---")

            st.subheader(f"📄 Processing: {file.name}")

            try:

                file.seek(0)

                data, full_text = process_invoice(file)

                final_data.append(data)

                # =================================================
                # OCR TEXT PREVIEW
                # =================================================

                with st.expander("📝 OCR Full Text"):

                    st.text(full_text[:5000])

                st.success("✅ Extraction Completed")

            except Exception as e:

                st.error(f"❌ Error Processing {file.name}")

                st.exception(e)

        # =====================================================
        # FINAL DATAFRAME
        # =====================================================

        df = pd.DataFrame(final_data)

        st.markdown("---")

        st.subheader("✅ Final Extracted Data")

        st.dataframe(
            df,
            use_container_width=True
        )

        # =====================================================
        # DOWNLOAD EXCEL
        # =====================================================

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine='xlsxwriter'
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name='Invoices'
            )

            worksheet = writer.sheets['Invoices']

            for i, col in enumerate(df.columns):

                column_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 5

                worksheet.set_column(
                    i,
                    i,
                    column_len
                )

        output.seek(0)

        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name="invoice_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
