# # app.py

# import streamlit as st
# import pandas as pd
# from io import BytesIO

# from invoice_processing import (
#     extract_text_from_pdf,
#     extract_invoice_data
# )

# # =====================================================
# # PAGE CONFIG
# # =====================================================

# st.set_page_config(
#     page_title="Invoice Extraction App",
#     layout="wide"
# )

# st.title("📄 Invoice Data Extraction")

# st.write("Upload one or multiple system-generated invoice PDFs")

# # =====================================================
# # FILE UPLOADER
# # =====================================================

# uploaded_files = st.file_uploader(
#     "Upload Invoice PDFs",
#     type=["pdf"],
#     accept_multiple_files=True
# )

# # =====================================================
# # PROCESS FILES
# # =====================================================

# if uploaded_files:

#     all_data = []

#     progress = st.progress(0)

#     for index, file in enumerate(uploaded_files):

#         st.write(f"Processing: {file.name}")

#         try:

#             # Extract text from PDF
#             text = extract_text_from_pdf(file)

#             # Extract invoice fields
#             data = extract_invoice_data(text)

#             # Add filename
#             data["File Name"] = file.name

#             # Append result
#             all_data.append(data)

#         except Exception as e:

#             st.error(f"Error processing {file.name}: {str(e)}")

#         progress.progress((index + 1) / len(uploaded_files))

#     # =====================================================
#     # CREATE DATAFRAME
#     # =====================================================

#     if all_data:

#         df = pd.DataFrame(all_data)

#         st.success("Invoices Processed Successfully")

#         st.dataframe(
#             df,
#             use_container_width=True
#         )

#         # =====================================================
#         # EXCEL DOWNLOAD
#         # =====================================================

#         output = BytesIO()

#         with pd.ExcelWriter(
#             output,
#             engine="xlsxwriter"
#         ) as writer:

#             df.to_excel(
#                 writer,
#                 index=False,
#                 sheet_name="Invoices"
#             )

#         excel_data = output.getvalue()

#         st.download_button(
#             label="📥 Download Excel",
#             data=excel_data,
#             file_name="invoice_output.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )







































# app.py

import streamlit as st
import pandas as pd
from io import BytesIO

from invoice_processing import (
    extract_text_from_pdf,
    extract_invoice_data
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Smart Invoice Extraction",
    layout="wide"
)

st.title("📄 Smart Invoice Extraction Engine")

st.write(
    """
Upload one or multiple system-generated invoice PDFs.

The engine intelligently detects:
- Invoice Number
- PO Number
- Invoice Date
- Taxable Amount
- Tax Amount
- Total Amount
- GST Numbers
- Vendor Name
"""
)

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_files = st.file_uploader(
    "Upload Invoice PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# =====================================================
# PROCESS FILES
# =====================================================

if uploaded_files:

    all_data = []

    progress = st.progress(0)

    for index, file in enumerate(uploaded_files):

        st.write(f"Processing: {file.name}")

        try:

            # Extract text
            text = extract_text_from_pdf(file)

            # Extract data
            data = extract_invoice_data(text)

            # Add filename
            data["File Name"] = file.name

            all_data.append(data)

        except Exception as e:

            st.error(f"Error processing {file.name}: {str(e)}")

        progress.progress((index + 1) / len(uploaded_files))

    # =====================================================
    # DATAFRAME
    # =====================================================

    if all_data:

        df = pd.DataFrame(all_data)

        st.success("Invoices Processed Successfully")

        st.dataframe(
            df,
            use_container_width=True
        )

        # =====================================================
        # EXCEL DOWNLOAD
        # =====================================================

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="xlsxwriter"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Invoices"
            )

        excel_data = output.getvalue()

        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="invoice_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
