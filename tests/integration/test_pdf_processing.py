from fastapi.testclient import TestClient

from app.main import app
from config import logger

from utils import MAX_FILE_SIZE


client = TestClient(app)


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
