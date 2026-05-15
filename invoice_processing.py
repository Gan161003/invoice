import re
import cv2
import numpy as np
import pandas as pd
import pdfplumber

from PIL import Image
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes

ocr = PaddleOCR(use_angle_cls=True, lang='en')


# =========================================
# OCR IMAGE
# =========================================

def extract_text_from_image(image):
    image_np = np.array(image)

    result = ocr.ocr(image_np)

    text = ""

    for line in result:
        for word in line:
            text += word[1][0] + " "

    return text


# =========================================
# OCR PDF
# =========================================

def extract_text_from_pdf(pdf_file):

    text = ""

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except:
        pass

    if len(text.strip()) > 20:
        return text

    images = convert_from_bytes(pdf_file.read())

    for image in images:
        text += extract_text_from_image(image)

    return text


# =========================================
# FIELD EXTRACTION
# =========================================

def extract_invoice_data(text):

    data = {}

    # Invoice Number
    invoice_patterns = [
        r"Invoice\s*No[:\-]?\s*(\S+)",
        r"Invoice\s*#[:\-]?\s*(\S+)",
        r"INV[- ]?\d+"
    ]

    invoice_no = ""

    for pattern in invoice_patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            invoice_no = match.group(1) if match.groups() else match.group(0)
            break

    # Date
    date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"

    date_match = re.search(date_pattern, text)

    invoice_date = date_match.group(0) if date_match else ""

    # GST
    gst_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b"

    gst_match = re.search(gst_pattern, text)

    gst = gst_match.group(0) if gst_match else ""

    # Total Amount
    amount_patterns = [
        r"Grand Total\s*[:\-]?\s*([\d,]+\.\d{2})",
        r"Total Amount\s*[:\-]?\s*([\d,]+\.\d{2})",
        r"Net Amount\s*[:\-]?\s*([\d,]+\.\d{2})"
    ]

    total_amount = ""

    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            total_amount = match.group(1)
            break

    data["Invoice Number"] = invoice_no
    data["Invoice Date"] = invoice_date
    data["GST Number"] = gst
    data["Total Amount"] = total_amount

    return data
