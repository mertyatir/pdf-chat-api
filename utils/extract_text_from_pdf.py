from config import logger
import pypdf
from io import BytesIO


def extract_text_from_pdf(pdf_content: bytes) -> str:
    if not pdf_content:
        logger.error("Empty PDF content provided.")
        raise ValueError("Empty PDF content provided.")
    pdf_stream = BytesIO(pdf_content)
    reader = pypdf.PdfReader(pdf_stream)
    page_count = reader.get_num_pages()
    extracted_text = ""
    for page_num in range(page_count):
        page = reader.get_page(page_num)
        extracted_text += page.extract_text()
    return extracted_text
