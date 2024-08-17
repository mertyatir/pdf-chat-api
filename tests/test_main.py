import pytest
import logging
from fastapi.testclient import TestClient
from app.main import app, MAX_FILE_SIZE, pdf_storage
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import requests
import pypdf

client = TestClient(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@pytest.fixture
def setup_valid_pdf():
    url = "https://www.jstage.jst.go.jp/article/jea1991/9/6sup/9_6sup_7/_pdf"
    file_path = "test.pdf"

    response = requests.get(url)
    with open(file_path, "wb") as f:
        f.write(response.content)

    with open(file_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        page_count = reader.get_num_pages()
        extracted_text = ""
        for page_num in range(page_count):
            page = reader.get_page(page_num)
            extracted_text += page.extract_text()

    pdf_id = "test-pdf-id"
    with open(file_path, "rb") as f:
        pdf_storage[pdf_id] = {
            "content": f.read(),
            "metadata": {
                "filename": os.path.basename(file_path),
                "document_id": pdf_id,
                "page_count": page_count,
                "extracted_text": extracted_text,
            },
        }

    yield pdf_id

    # Teardown
    pdf_storage.pop(pdf_id, None)
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


def test_upload_valid_pdf(setup_valid_pdf):
    with open("test.pdf", "rb") as f:
        response = client.post(
            "/v1/pdf", files={"file": ("test.pdf", f, "application/pdf")}
        )
    logger.info("Response: %s", response.json())
    assert response.status_code == 200
    assert "pdf_id" in response.json()


def test_upload_invalid_file_type(setup_invalid_file):
    with open("test.txt", "rb") as f:
        response = client.post(
            "/v1/pdf", files={"file": ("test.txt", f, "text/plain")}
        )
    logger.info("Response: %s", response.json())
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid file type. Only PDF files are allowed."
    }


def test_upload_invalid_content_type(setup_valid_pdf):
    with open("test.pdf", "rb") as f:
        response = client.post(
            "/v1/pdf", files={"file": ("test.pdf", f, "text/plain")}
        )
    logger.info("Response: %s", response.json())
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid content type. Only PDF files are allowed."
    }


def test_upload_file_size_exceeds_limit(setup_large_pdf):
    with open("large.pdf", "rb") as f:
        response = client.post(
            "/v1/pdf", files={"file": ("large.pdf", f, "application/pdf")}
        )
    logger.info("Response: %s", response.json())
    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            f"File size exceeds the limit of "
            f"{MAX_FILE_SIZE / (1024 * 1024)} MB."
        )
    }


def test_upload_multi_page_pdf(setup_multi_page_pdf):
    with open("multi_page.pdf", "rb") as f:
        response = client.post(
            "/v1/pdf", files={"file": ("multi_page.pdf", f, "application/pdf")}
        )
    logger.info("Response: %s", response.json())
    assert response.status_code == 200
    response_data = response.json()
    assert "pdf_id" in response.json()
    pdf_id = response_data["pdf_id"]
    assert pdf_storage[pdf_id]["metadata"]["page_count"] == 3


def test_chat_with_pdf_valid(setup_valid_pdf):
    pdf_id = setup_valid_pdf
    message = {"message": "What is this PDF about?"}

    response = client.post(f"/v1/chat/{pdf_id}", json=message)
    assert response.status_code == 200
    logger.info("Response: %s", response.json())
