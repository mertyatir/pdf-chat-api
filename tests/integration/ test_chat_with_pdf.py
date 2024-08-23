from config.logger import logger
import pytest
from fastapi.testclient import TestClient
from app.main import app

from tests.test_utils import create_and_upload_test_pdf


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_chat_with_pdf(client: TestClient):

    response = create_and_upload_test_pdf(client)

    pdf_id = response.json()["pdf_id"]
    message = "Hello World!"

    response = client.post(f"/v1/chat/{pdf_id}/", json={"message": message})
    logger.info(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "response" in response.json()
