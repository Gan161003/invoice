# # # invoice_processing.py

# # import re
# # import fitz
# # import pdfplumber

# # # =====================================================
# # # PDF TEXT EXTRACTION
# # # =====================================================

# # def extract_text_from_pdf(pdf_file):

# #     text = ""

# #     # Read PDF bytes
# #     pdf_bytes = pdf_file.read()

# #     # ---------------------------------------------
# #     # METHOD 1 : PyMuPDF
# #     # ---------------------------------------------

# #     try:

# #         doc = fitz.open(
# #             stream=pdf_bytes,
# #             filetype="pdf"
# #         )

# #         for page in doc:

# #             text += page.get_text()

# #     except:
# #         pass

# #     # ---------------------------------------------
# #     # METHOD 2 : pdfplumber fallback
# #     # ---------------------------------------------

# #     if len(text.strip()) < 20:

# #         try:

# #             pdf_file.seek(0)

# #             with pdfplumber.open(pdf_file) as pdf:

# #                 for page in pdf.pages:

# #                     page_text = page.extract_text()

# #                     if page_text:
# #                         text += page_text + "\n"

# #         except:
# #             pass

# #     return text


# # # =====================================================
# # # CLEAN AMOUNT
# # # =====================================================

# # def clean_amount(value):

# #     if not value:
# #         return ""

# #     value = value.replace(",", "")
# #     value = value.replace("₹", "")
# #     value = value.strip()

# #     return value


# # # =====================================================
# # # FIND MATCH
# # # =====================================================

# # def find_match(patterns, text):

# #     for pattern in patterns:

# #         match = re.search(
# #             pattern,
# #             text,
# #             re.IGNORECASE
# #         )

# #         if match:

# #             if match.groups():
# #                 return match.group(1).strip()

# #             return match.group(0).strip()

# #     return ""


# # # =====================================================
# # # EXTRACT INVOICE DATA
# # # =====================================================

# # def extract_invoice_data(text):

# #     data = {}

# #     # =================================================
# #     # INVOICE NUMBER
# #     # =================================================

# #     invoice_patterns = [

# #         r"Invoice\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
# #         r"Invoice\s*Num\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
# #         r"Invoice\s*Number\s*[:\-]?\s*([A-Z0-9\/\-]+)",
# #         r"Inv\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)"

# #     ]

# #     invoice_no = find_match(
# #         invoice_patterns,
# #         text
# #     )

# #     # =================================================
# #     # PO NUMBER
# #     # =================================================

# #     po_patterns = [

# #         r"PO\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
# #         r"PO\s*Num\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
# #         r"PO\s*Number\s*[:\-]?\s*([A-Z0-9\/\-]+)",
# #         r"Purchase\s*Order\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)"

# #     ]

# #     po_number = find_match(
# #         po_patterns,
# #         text
# #     )

# #     # =================================================
# #     # DATE
# #     # =================================================

# #     date_patterns = [

# #         r"\b\d{2}/\d{2}/\d{4}\b",
# #         r"\b\d{2}-\d{2}-\d{4}\b",
# #         r"\b\d{2}\.\d{2}\.\d{4}\b",
# #         r"\b\d{4}-\d{2}-\d{2}\b"

# #     ]

# #     invoice_date = find_match(
# #         date_patterns,
# #         text
# #     )

# #     # =================================================
# #     # GST NUMBER
# #     # =================================================

# #     gst_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b"

# #     gst_match = re.search(
# #         gst_pattern,
# #         text
# #     )

# #     gst_number = gst_match.group(0) if gst_match else ""

# #     # =================================================
# #     # AMOUNT WITHOUT TAX
# #     # =================================================

# #     subtotal_patterns = [

# #         r"Sub\s*Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Taxable\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Basic\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Amount\s*Before\s*Tax\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"

# #     ]

# #     amount_without_tax = clean_amount(
# #         find_match(
# #             subtotal_patterns,
# #             text
# #         )
# #     )

# #     # =================================================
# #     # TAX AMOUNT
# #     # =================================================

# #     tax_patterns = [

# #         r"GST\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Tax\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Total\s*Tax\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"

# #     ]

# #     tax_amount = clean_amount(
# #         find_match(
# #             tax_patterns,
# #             text
# #         )
# #     )

# #     # =================================================
# #     # TOTAL AMOUNT WITH TAX
# #     # =================================================Total Payable (A+B)

# #     total_patterns = [

# #         r"Grand\s*Total\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Invoice\s*Value\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Net\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Total\s*Amount\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})",
# #         r"Total\s*Payable\s*[:\-]?\s*₹?\s*([\d,]+\.\d{2})"

# #     ]

# #     total_amount = clean_amount(
# #         find_match(
# #             total_patterns,
# #             text
# #         )
# #     )

# #     # =================================================
# #     # VENDOR NAME
# #     # =================================================

# #     lines = text.split("\n")

# #     vendor_name = ""

# #     for line in lines[:15]:

# #         line = line.strip()

# #         if (
# #             len(line) > 5
# #             and "invoice" not in line.lower()
# #             and "tax" not in line.lower()
# #         ):

# #             vendor_name = line
# #             break

# #     # =================================================
# #     # EMAIL
# #     # =================================================

# #     email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

# #     email_match = re.search(
# #         email_pattern,
# #         text
# #     )

# #     email = email_match.group(0) if email_match else ""

# #     # =================================================
# #     # PHONE
# #     # =================================================

# #     phone_pattern = r"\b\d{10}\b"

# #     phone_match = re.search(
# #         phone_pattern,
# #         text
# #     )

# #     phone = phone_match.group(0) if phone_match else ""

# #     # =================================================
# #     # STORE DATA
# #     # =================================================

# #     data["Vendor Name"] = vendor_name
# #     data["Invoice Number"] = invoice_no
# #     data["PO Number"] = po_number
# #     data["Invoice Date"] = invoice_date
# #     data["GST Number"] = gst_number
# #     data["Amount Without Tax"] = amount_without_tax
# #     data["Tax Amount"] = tax_amount
# #     data["Total Amount With Tax"] = total_amount
# #     data["Vendor Email"] = email
# #     data["Vendor Phone"] = phone

# #     return data








# # invoice_processing.py

# import re
# import fitz
# import pdfplumber


# # =====================================================
# # PDF TEXT EXTRACTION
# # =====================================================

# def extract_text_from_pdf(pdf_file):

#     text = ""

#     pdf_bytes = pdf_file.read()

#     # ---------------------------------------------
#     # METHOD 1 : PyMuPDF
#     # ---------------------------------------------

#     try:

#         doc = fitz.open(
#             stream=pdf_bytes,
#             filetype="pdf"
#         )

#         for page in doc:

#             text += page.get_text() + "\n"

#     except Exception:
#         pass

#     # ---------------------------------------------
#     # METHOD 2 : pdfplumber fallback
#     # ---------------------------------------------

#     if len(text.strip()) < 20:

#         try:

#             pdf_file.seek(0)

#             with pdfplumber.open(pdf_file) as pdf:

#                 for page in pdf.pages:

#                     page_text = page.extract_text()

#                     if page_text:
#                         text += page_text + "\n"

#         except Exception:
#             pass

#     return text


# # =====================================================
# # CLEAN AMOUNT
# # =====================================================

# def clean_amount(value):

#     if not value:
#         return ""

#     value = str(value)

#     value = value.replace(",", "")
#     value = value.replace("₹", "")
#     value = value.replace("Rs.", "")
#     value = value.replace("INR", "")

#     value = value.strip()

#     return value


# # =====================================================
# # FIND MATCH
# # =====================================================

# def find_match(patterns, text):

#     for pattern in patterns:

#         match = re.search(
#             pattern,
#             text,
#             re.IGNORECASE | re.MULTILINE
#         )

#         if match:

#             if match.groups():
#                 return match.group(1).strip()

#             return match.group(0).strip()

#     return ""


# # =====================================================
# # EXTRACT AMOUNT
# # =====================================================

# def extract_amount(patterns, text):

#     value = find_match(patterns, text)

#     return clean_amount(value)


# # =====================================================
# # EXTRACT INVOICE DATA
# # =====================================================

# def extract_invoice_data(text):

#     data = {}

#     # =================================================
#     # VENDOR NAME
#     # =================================================

#     vendor_patterns = [

#         r"Tax Invoice.*?\n([A-Za-z0-9\s\.\&\-,]+)",
#         r"\n([A-Za-z0-9\s\.\&\-,]+Pvt Ltd)",
#         r"\n([A-Za-z0-9\s\.\&\-,]+Private Limited)",
#         r"\n([A-Za-z0-9\s\.\&\-,]+Ltd)"

#     ]

#     vendor_name = find_match(
#         vendor_patterns,
#         text
#     )

#     # =================================================
#     # INVOICE NUMBER
#     # =================================================

#     invoice_patterns = [

#         r"Invoice\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"Invoice\s*Num\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"Invoice\s*Number\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"Bill\s*Number\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"MM\d+[A-Z0-9]+"

#     ]

#     invoice_no = find_match(
#         invoice_patterns,
#         text
#     )

#     # =================================================
#     # PO NUMBER
#     # =================================================

#     po_patterns = [

#         r"PO\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"PO\s*Num\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"PO\s*Number\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"Purchase\s*Order\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)"

#     ]

#     po_number = find_match(
#         po_patterns,
#         text
#     )

#     # =================================================
#     # ESTIMATE NUMBER
#     # =================================================

#     est_patterns = [

#         r"Est\.?\s*Num\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)",
#         r"Estimate\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-]+)"

#     ]

#     estimate_number = find_match(
#         est_patterns,
#         text
#     )

#     # =================================================
#     # BRAND
#     # =================================================

#     brand_patterns = [

#         r"Brand\s*[:\-]?\s*([A-Za-z0-9\s\&\-]+)"

#     ]

#     brand_name = find_match(
#         brand_patterns,
#         text
#     )

#     # =================================================
#     # CLIENT NAME
#     # =================================================

#     client_patterns = [

#         r"Client\s*[:\-]?\s*([A-Za-z0-9\s\&\-,]+)",
#         r"Buyer Address\s*\n([A-Za-z0-9\s\&\-,]+)"

#     ]

#     client_name = find_match(
#         client_patterns,
#         text
#     )

#     # =================================================
#     # INVOICE DATE
#     # =================================================

#     invoice_date_patterns = [

#         r"Invoice\s*Date\s*[:\-]?\s*([0-9]{1,2}\s[A-Za-z]{3}\s[0-9]{4})",
#         r"Invoice\s*Date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})",
#         r"Invoice\s*Date\s*[:\-]?\s*(\d{2}-\d{2}-\d{4})"

#     ]

#     invoice_date = find_match(
#         invoice_date_patterns,
#         text
#     )

#     # =================================================
#     # DUE DATE
#     # =================================================

#     due_date_patterns = [

#         r"Due\s*Date\s*[:\-]?\s*([0-9]{1,2}\s[A-Za-z]{3}\s[0-9]{4})",
#         r"Due\s*Date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})"

#     ]

#     due_date = find_match(
#         due_date_patterns,
#         text
#     )

#     # =================================================
#     # GST NUMBER
#     # =================================================

#     gst_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b"

#     gst_numbers = re.findall(
#         gst_pattern,
#         text
#     )

#     vendor_gst = gst_numbers[0] if len(gst_numbers) > 0 else ""
#     client_gst = gst_numbers[1] if len(gst_numbers) > 1 else ""

#     # =================================================
#     # PAN NUMBER
#     # =================================================

#     pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

#     pan_numbers = re.findall(
#         pan_pattern,
#         text
#     )

#     vendor_pan = pan_numbers[0] if len(pan_numbers) > 0 else ""
#     client_pan = pan_numbers[1] if len(pan_numbers) > 1 else ""

#     # =================================================
#     # TAXABLE AMOUNT
#     # =================================================

#     taxable_patterns = [

#         r"Taxable\s*Amount\s*[:\-]?\s*([\d,]+\.\d{2})",
#         r"Amount\s*Before\s*Tax\s*[:\-]?\s*([\d,]+\.\d{2})",
#         r"Sub\s*Total\s*[:\-]?\s*([\d,]+\.\d{2})"

#     ]

#     taxable_amount = extract_amount(
#         taxable_patterns,
#         text
#     )

#     # =================================================
#     # SGST
#     # =================================================

#     sgst_patterns = [

#         r"SGST\s*@.*?\s([\d,]+\.\d{2})"

#     ]

#     sgst_amount = extract_amount(
#         sgst_patterns,
#         text
#     )

#     # =================================================
#     # CGST
#     # =================================================

#     cgst_patterns = [

#         r"CGST\s*@.*?\s([\d,]+\.\d{2})"

#     ]

#     cgst_amount = extract_amount(
#         cgst_patterns,
#         text
#     )

#     # =================================================
#     # TOTAL TAX
#     # =================================================

#     total_tax = ""

#     try:

#         total_tax = str(
#             round(
#                 float(sgst_amount or 0) +
#                 float(cgst_amount or 0),
#                 2
#             )
#         )

#     except:
#         total_tax = ""

#     # =================================================
#     # TOTAL PAYABLE
#     # =================================================

#     total_patterns = [

#         r"Total\s*Payable\s*\(A\+B\)\s*[:\-]?\s*([\d,]+\.\d{2})",
#         r"Grand\s*Total\s*[:\-]?\s*([\d,]+\.\d{2})",
#         r"Invoice\s*Value\s*[:\-]?\s*([\d,]+\.\d{2})",
#         r"Net\s*Amount\s*[:\-]?\s*([\d,]+\.\d{2})"

#     ]

#     total_amount = extract_amount(
#         total_patterns,
#         text
#     )

#     # =================================================
#     # EMAIL
#     # =================================================

#     email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

#     emails = re.findall(
#         email_pattern,
#         text
#     )

#     vendor_email = emails[0] if len(emails) > 0 else ""

#     # =================================================
#     # PHONE
#     # =================================================

#     phone_pattern = r"\b\d{10}\b"

#     phones = re.findall(
#         phone_pattern,
#         text
#     )

#     phone = phones[0] if len(phones) > 0 else ""

#     # =================================================
#     # STORE DATA
#     # =================================================

#     data["Vendor Name"] = vendor_name
#     data["Client Name"] = client_name
#     data["Brand"] = brand_name

#     data["Invoice Number"] = invoice_no
#     data["PO Number"] = po_number
#     data["Estimate Number"] = estimate_number

#     data["Invoice Date"] = invoice_date
#     data["Due Date"] = due_date

#     data["Vendor GST"] = vendor_gst
#     data["Client GST"] = client_gst

#     data["Vendor PAN"] = vendor_pan
#     data["Client PAN"] = client_pan

#     data["Amount Without Tax"] = taxable_amount

#     data["SGST Amount"] = sgst_amount
#     data["CGST Amount"] = cgst_amount

#     data["Total Tax Amount"] = total_tax

#     data["Total Amount With Tax"] = total_amount

#     data["Vendor Email"] = vendor_email
#     data["Vendor Phone"] = phone

#     return data
















































# invoice_processing.py

import re
import fitz
import pdfplumber
from difflib import SequenceMatcher

# =====================================================
# LABEL DEFINITIONS
# =====================================================

FIELD_LABELS = {

    "invoice_number": [
        "invoice no",
        "invoice number",
        "invoice #",
        "bill no",
        "bill number",
        "reference no",
        "invoice num"
    ],

    "po_number": [
        "po no",
        "po number",
        "purchase order",
        "purchase order no",
        "po num"
    ],

    "invoice_date": [
        "invoice date",
        "bill date",
        "date"
    ],

    "due_date": [
        "due date",
        "payment due"
    ],

    "taxable_amount": [
        "taxable amount",
        "amount before tax",
        "subtotal",
        "basic amount",
        "net amount"
    ],

    "total_amount": [
        "grand total",
        "invoice value",
        "total payable",
        "total amount",
        "gross amount"
    ]
}


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_text_from_pdf(pdf_file):

    text = ""

    pdf_bytes = pdf_file.read()

    # ---------------------------------------------
    # METHOD 1 : PYMUPDF
    # ---------------------------------------------

    try:

        doc = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        for page in doc:

            text += page.get_text() + "\n"

    except:
        pass

    # ---------------------------------------------
    # METHOD 2 : PDFPLUMBER
    # ---------------------------------------------

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
# FUZZY MATCH
# =====================================================

def similarity(a, b):

    return SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()


# =====================================================
# FIND VALUE NEAR LABEL
# =====================================================
def find_value_near_label(text, possible_labels):

    lines = text.split("\n")

    for line in lines:

        clean_line = line.lower().strip()

        # normalize spaces
        clean_line = re.sub(r"\s+", " ", clean_line)

        for label in possible_labels:

            label = label.lower().strip()

            # DIRECT LABEL MATCH
            if label in clean_line:

                # -----------------------------------
                # AFTER :
                # -----------------------------------

                if ":" in line:

                    parts = line.split(":", 1)

                    if len(parts) > 1:

                        value = parts[1].strip()

                        if value:
                            return value

                # -----------------------------------
                # AFTER -
                # -----------------------------------

                if "-" in line:

                    parts = line.split("-", 1)

                    if len(parts) > 1:

                        value = parts[1].strip()

                        if value:
                            return value

                # -----------------------------------
                # AFTER LABEL
                # -----------------------------------

                pattern = re.escape(label) + r"\s*(.*)"

                match = re.search(
                    pattern,
                    clean_line,
                    re.IGNORECASE
                )

                if match:

                    value = match.group(1).strip()

                    if value:
                        return value

    return ""


# =====================================================
# EXTRACT DATE
# =====================================================

def extract_date(value):

    date_patterns = [

        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{4}-\d{2}-\d{2}",
        r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}",
        r"\d{1,2}\s+[A-Za-z]+\s+\d{4}"
    
    ]

    for pattern in date_patterns:

        match = re.search(pattern, value)

        if match:
            return match.group(0)

    return ""


# =====================================================
# EXTRACT AMOUNT
# =====================================================

def extract_amount(value):

    amount_pattern = r"[\d,]+\.\d{2}"

    match = re.search(amount_pattern, value)

    if match:

        amount = match.group(0)

        amount = amount.replace(",", "")

        return amount

    return ""


# =====================================================
# GST EXTRACTION
# =====================================================

def extract_gst(text):

    gst_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b"

    gst_numbers = re.findall(
        gst_pattern,
        text
    )

    if gst_numbers:
        return gst_numbers[0]

    return ""


# =====================================================
# EMAIL EXTRACTION
# =====================================================

def extract_email(text):

    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    emails = re.findall(
        email_pattern,
        text
    )

    if emails:
        return emails[0]

    return ""


# =====================================================
# VENDOR NAME
# =====================================================

def extract_vendor_name(text):

    lines = text.split("\n")

    for line in lines[:10]:

        line = line.strip()

        if (
            len(line) > 5
            and "invoice" not in line.lower()
            and "gst" not in line.lower()
            and "tax" not in line.lower()
        ):

            return line

    return ""


# =====================================================
# MAIN EXTRACTION
# =====================================================

def extract_invoice_data(text):

    data = {}

    # =================================================
    # INVOICE NUMBER
    # =================================================

    invoice_number = find_value_near_label(
        text,
        FIELD_LABELS["invoice_number"]
    )

    # =================================================
    # PO NUMBER
    # =================================================

    po_number = find_value_near_label(
        text,
        FIELD_LABELS["po_number"]
    )

    # =================================================
    # INVOICE DATE
    # =================================================

    invoice_date_raw = find_value_near_label(
        text,
        FIELD_LABELS["invoice_date"]
    )

    invoice_date = extract_date(
        invoice_date_raw
    )

    # =================================================
    # DUE DATE
    # =================================================

    due_date_raw = find_value_near_label(
        text,
        FIELD_LABELS["due_date"]
    )

    due_date = extract_date(
        due_date_raw
    )

    # =================================================
    # TAXABLE AMOUNT
    # =================================================

    taxable_amount_raw = find_value_near_label(
        text,
        FIELD_LABELS["taxable_amount"]
    )

    taxable_amount = extract_amount(
        taxable_amount_raw
    )

    # =================================================
    # TOTAL AMOUNT
    # =================================================

    total_amount_raw = find_value_near_label(
        text,
        FIELD_LABELS["total_amount"]
    )

    total_amount = extract_amount(
        total_amount_raw
    )

    # =================================================
    # GST
    # =================================================

    gst_number = extract_gst(text)

    # =================================================
    # EMAIL
    # =================================================

    email = extract_email(text)

    # =================================================
    # VENDOR NAME
    # =================================================

    vendor_name = extract_vendor_name(text)

    # =================================================
    # TAX CALCULATION
    # =================================================

    tax_amount = ""

    try:

        if taxable_amount and total_amount:

            tax_amount = str(
                round(
                    float(total_amount) -
                    float(taxable_amount),
                    2
                )
            )

    except:
        pass

    # =================================================
    # STORE DATA
    # =================================================

    data["Vendor Name"] = vendor_name
    data["Invoice Number"] = invoice_number
    data["PO Number"] = po_number
    data["Invoice Date"] = invoice_date
    data["Due Date"] = due_date
    data["GST Number"] = gst_number
    data["Amount Without Tax"] = taxable_amount
    data["Tax Amount"] = tax_amount
    data["Total Amount With Tax"] = total_amount
    data["Vendor Email"] = email

    return data
