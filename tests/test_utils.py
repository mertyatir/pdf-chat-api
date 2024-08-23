from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config.logger import logger


def create_test_pdf(file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "This is a test PDF file.")
    c.save()


def create_and_upload_test_pdf(client):
    create_test_pdf("tests/test.pdf")

    with open("tests/test.pdf", "rb") as f:
        file_content = f.read()

    response = client.post(
        "/v1/pdf/",
        files={"file": ("tests/test.pdf", file_content, "application/pdf")},
    )

    logger.info(f"Response: {response.json()}")

    return response
