from fastapi.testclient import TestClient
from app.main import app
from config import logger


client = TestClient(app)


def test_chat_with_pdf_valid(setup_valid_pdf):
    pdf_id = setup_valid_pdf
    message = {"message": "What is this PDF about?"}

    response = client.post(f"/v1/chat/{pdf_id}/", json=message)
    assert response.status_code == 200
    logger.info("Response: %s", response.json())
