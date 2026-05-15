# invoice_processing.py

import re
import fitz
import pdfplumber

# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_text_from_pdf(pdf_file):

    text = ""

    # Read PDF bytes
    pdf_bytes = pdf_file.read()

    # =========================================
    # METHOD 1 - PYMUPDF
    # =========================================

    try:

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:

            text += page.get_text()

    except:
        pass

    # =========================================
    # METHOD 2 - PDFPLUMBER FALLBACK
    # =========================================

    if len(text.strip()) < 20:

        try:

            pdf_file.seek(0)

            with pdfplumber.open(pdf_file) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

        except:
            pass

    return text


# =====================================================
# FIELD EXTRACTION
# =====================================================

def extract_invoice_data(text):

    data = {}

    # =========================================
    # INVOICE NUMBER
    # =========================================

    invoice_patterns = [

        r"Invoice\s*No[:\-]?\s*([A-Z0-9\-\/]+)",
        r"Invoice\s*#[:\-]?\s*([A-Z0-9\-\/]+)",
        r"Inv\s*No[:\-]?\s*([A-Z0-9\-\/]+)"

    ]

    invoice_no = ""

    for pattern in invoice_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            invoice_no = match.group(1)

            break

    # =========================================
    # DATE
    # =========================================

    date_patterns = [

        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{2}-\d{2}-\d{4}\b",
        r"\b\d{2}\.\d{2}\.\d{2024}\b"

    ]

    invoice_date = ""

    for pattern in date_patterns:

        match = re.search(pattern, text)

        if match:

            invoice_date = match.group(0)

            break

    # =========================================
    # GST NUMBER
    # =========================================

    gst_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b"

    gst_match = re.search(gst_pattern, text)

    gst_number = gst_match.group(0) if gst_match else ""

    # =========================================
    # TOTAL AMOUNT
    # =========================================

    amount_patterns = [

        r"Grand\s*Total[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Total\s*Amount[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Invoice\s*Value[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Net\s*Amount[:\-]?\s*₹?\s*([\d,]+\.\d{2})"

    ]

    total_amount = ""

    for pattern in amount_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            total_amount = match.group(1)

            break

    # =========================================
    # VENDOR NAME
    # =========================================

    lines = text.split("\n")

    vendor_name = ""

    for line in lines[:10]:

        line = line.strip()

        if len(line) > 5:

            vendor_name = line

            break

    # =========================================
    # STORE DATA
    # =========================================

    data["Vendor Name"] = vendor_name
    data["Invoice Number"] = invoice_no
    data["Invoice Date"] = invoice_date
    data["GST Number"] = gst_number
    data["Total Amount"] = total_amount

    return data
