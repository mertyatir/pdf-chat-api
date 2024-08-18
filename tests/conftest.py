import pytest
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import requests
import pypdf
from config import SessionLocal
from models import PDFFile
from utils import MAX_FILE_SIZE
import uuid


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


test_pdf_url = (
    "https://www.hilldale.k12.ok.us/vimages/shared"
    + "/vnews/stories/565f3ab905b1d/color.pdf"
)


@pytest.fixture
def setup_valid_pdf(db_session):
    url = test_pdf_url
    file_path = "test.pdf"

    response = requests.get(url)
    with open(file_path, "wb") as f:
        f.write(response.content)

    with open(file_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        page_count = reader.get_num_pages()

    pdf_id = str(uuid.uuid4())
    with open(file_path, "rb") as f:
        pdf_file = PDFFile(
            id=pdf_id,
            filename=os.path.basename(file_path),
            page_count=page_count,
            content=f.read(),
        )
        db_session.add(pdf_file)
        db_session.commit()

    yield pdf_id

    # Teardown
    db_session.delete(pdf_file)
    db_session.commit()
    os.remove(file_path)


@pytest.fixture
def setup_invalid_file():
    with open("test.txt", "wb") as f:
        f.write(b"Hello, World!")
    yield
    os.remove("test.txt")


@pytest.fixture
def setup_large_pdf():
    file_path = "large.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "This is a large PDF file.")
    c.save()
    with open(file_path, "ab") as f:
        f.write(b"0" * (MAX_FILE_SIZE + 1 - os.path.getsize(file_path)))
    yield
    os.remove(file_path)


@pytest.fixture
def setup_multi_page_pdf():
    file_path = "multi_page.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    for i in range(3):
        c.drawString(100, 750, f"Page {i + 1}")
        c.showPage()
    c.save()
    yield
    os.remove(file_path)
