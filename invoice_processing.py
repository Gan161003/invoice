import re
import pandas as pd
from pdf2image import convert_from_bytes
from paddleocr import PaddleOCR

# =========================================================
# LOAD OCR MODEL
# =========================================================

ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en'
)

# =========================================================
# KEYWORDS
# =========================================================

FIELD_KEYWORDS = {

    "Invoice Num": [
        "invoice no",
        "invoice num",
        "invoice number"
    ],

    "PO Num": [
        "po no",
        "po num",
        "purchase order",
        "po number"
    ],

    "Taxable Amount": [
        "taxable amount",
        "subtotal",
        "net amount"
    ],

    "Total Payable (A+B)": [
        "total payable",
        "grand total",
        "invoice total",
        "amount due"
    ]
}

# =========================================================
# REGEX PATTERNS
# =========================================================

AMOUNT_PATTERN = r'[\d,]+\.\d{2}'

PO_PATTERN = r'PO\/[\w\-\/]+'

# =========================================================
# OCR TEXT EXTRACTION
# =========================================================

def extract_text_from_pdf(uploaded_file):

    pdf_bytes = uploaded_file.read()

    images = convert_from_bytes(pdf_bytes)

    full_text = []

    for image in images:

        result = ocr.ocr(image)

        if result and result[0]:

            for line in result[0]:

                text = line[1][0]

                full_text.append(text)

    return "\n".join(full_text)

# =========================================================
# FIND FIELD LINE
# =========================================================

def find_line(text, keywords):

    lines = text.split("\n")

    for line in lines:

        lower_line = line.lower()

        for keyword in keywords:

            if keyword in lower_line:

                return line

    return ""

# =========================================================
# CLEAN AMOUNT
# =========================================================

def clean_amount(value):

    if not value:

        return ""

    match = re.search(
        AMOUNT_PATTERN,
        value
    )

    if match:

        return match.group()

    return value

# =========================================================
# CLEAN PO
# =========================================================

def clean_po(value):

    match = re.search(
        PO_PATTERN,
        value,
        re.IGNORECASE
    )

    if match:

        return match.group()

    return value

# =========================================================
# EXTRACT FIELD VALUE
# =========================================================

def extract_field_value(field, line):

    if not line:

        return ""

    if ":" in line:

        value = line.split(":")[-1].strip()

    else:

        value = line.strip()

    if field in [
        "Taxable Amount",
        "Total Payable (A+B)"
    ]:

        value = clean_amount(value)

    if field == "PO Num":

        value = clean_po(value)

    return value

# =========================================================
# PROCESS PDFS
# =========================================================

def process_invoice_pdfs(invoice_files):

    final_data = []

    for file in invoice_files:

        try:

            file.seek(0)

            full_text = extract_text_from_pdf(file)

            row = {}

            for field, keywords in FIELD_KEYWORDS.items():

                matched_line = find_line(
                    full_text,
                    keywords
                )

                value = extract_field_value(
                    field,
                    matched_line
                )

                row[field] = value

            row["File Name"] = file.name

            final_data.append(row)

        except Exception as e:

            final_data.append({
                "File Name": file.name,
                "Error": str(e)
            })

    df = pd.DataFrame(final_data)

    return df
