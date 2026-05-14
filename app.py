import streamlit as st
import pandas as pd
from io import BytesIO

from invoice_processing import process_invoice_pdfs

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Invoice OCR",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("📄 AI Invoice OCR Engine")

st.markdown("---")

# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_pdfs = st.file_uploader(
    "Upload Invoice PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# =========================================================
# PROCESS
# =========================================================

if uploaded_pdfs:

    st.success(f"{len(uploaded_pdfs)} PDFs Uploaded")

    if st.button("🚀 Process Invoices"):

        with st.spinner("Processing PDFs..."):

            df = process_invoice_pdfs(uploaded_pdfs)

        # =================================================
        # SHOW OUTPUT
        # =================================================

        st.subheader("✅ Extracted Invoice Data")

        st.dataframe(
            df,
            use_container_width=True
        )

        # =================================================
        # DOWNLOAD EXCEL
        # =================================================

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

                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 5

                worksheet.set_column(
                    i,
                    i,
                    max_len
                )

        output.seek(0)

        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name="invoice_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
