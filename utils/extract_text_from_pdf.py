from typing import BinaryIO
import pypdf


def extract_text_from_pdf(file: BinaryIO) -> str:
    reader = pypdf.PdfReader(file)
    page_count = reader.get_num_pages()
    extracted_text = ""
    for page_num in range(page_count):
        page = reader.get_page(page_num)
        extracted_text += page.extract_text()
    return extracted_text
