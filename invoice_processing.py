# invoice_processing.py

import re
import fitz
import pdfplumber

# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_text_from_pdf(pdf_file):

    text = ""

    pdf_bytes = pdf_file.read()

    # -----------------------------------------
    # METHOD 1 : PYMUPDF
    # -----------------------------------------

    try:

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:

            text += page.get_text()

    except:
        pass

    # -----------------------------------------
    # METHOD 2 : PDFPLUMBER FALLBACK
    # -----------------------------------------

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
# CLEAN AMOUNT
# =====================================================

def clean_amount(value):

    if not value:
        return ""

    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.strip()

    return value


# =====================================================
# FIND FIRST MATCH
# =====================================================

def find_match(patterns, text):

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            if match.groups():
                return match.group(1).strip()

            return match.group(0).strip()

    return ""


# =====================================================
# EXTRACT INVOICE DATA
# =====================================================

def extract_invoice_data(text):

    data = {}

    # =================================================
    # INVOICE NUMBER
    # =================================================

    invoice_patterns = [

        r"Invoice\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
        r"Invoice\s*Number\s*[:\-]?\s*([A-Z0-9\/\-]+)",
        r"Inv\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)"

    ]

    invoice_no = find_match(invoice_patterns, text)

    # =================================================
    # PO NUMBER
    # =================================================

    po_patterns = [

        r"PO\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
        r"PO\s*Number\s*[:\-]?\s*([A-Z0-9\/\-]+)",
        r"Purchase\s*Order\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)"

    ]

    po_number = find_match(po_patterns, text)

    # =================================================
    # DATE
    # =================================================

    date_patterns = [

        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{2}-\d{2}-\d{4}\b",
        r"\b\d{2}\.\d{2}\.\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b"

    ]

    invoice_date = find_match(date_patterns, text)

    # =================================================
    # GST NUMBER
    # =================================================

    gst_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b"

    gst_match = re.search(gst_pattern, text)

    gst_number = gst_match.group(0) if gst_match else ""

    # =================================================
    # AMOUNT WITHOUT TAX
    # =================================================

    subtotal_patterns = [

        r"Sub\s*Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Taxable\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Basic\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Amount\s*Before\s*Tax\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"

    ]

    amount_without_tax = clean_amount(
        find_match(subtotal_patterns, text)
    )

    # =================================================
    # TAX AMOUNT
    # =================================================

    tax_patterns = [

        r"GST\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Tax\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Total\s*Tax\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"

    ]

    tax_amount = clean_amount(
        find_match(tax_patterns, text)
    )

    # =================================================
    # TOTAL AMOUNT WITH TAX
    # =================================================

    total_patterns = [

        r"Grand\s*Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Invoice\s*Value\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Net\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
        r"Total\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"

    ]

    total_amount = clean_amount(
        find_match(total_patterns, text)
    )

    # =================================================
    # VENDOR NAME
    # =================================================

    lines = text.split("\n")

    vendor_name = ""

    for line in lines[:15]:

        line = line.strip()

        if (
            len(line) > 5
            and "invoice" not in line.lower()
            and "tax" not in line.lower()
        ):

            vendor_name = line
            break

    # =================================================
    # EMAIL
    # =================================================

    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    email_match = re.search(email_pattern, text)

    email = email_match.group(0) if email_match else ""

    # =================================================
    # PHONE
    # =================================================

    phone_pattern = r"\b\d{10}\b"

    phone_match = re.search(phone_pattern, text)

    phone = phone_match.group(0) if phone_match else ""

    # =================================================
    # STORE DATA
    # =================================================

    data["Vendor Name"] = vendor_name
    data["Invoice Number"] = invoice_no
    data["PO Number"] = po_number
    data["Invoice Date"] = invoice_date
    data["GST Number"] = gst_number
    data["Amount Without Tax"] = amount_without_tax
    data["Tax Amount"] = tax_amount
    data["Total Amount With Tax"] = total_amount
    data["Vendor Email"] = email
    data["Vendor Phone"] = phone

    return data
