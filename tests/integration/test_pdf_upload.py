import pytest
from fastapi.testclient import TestClient
from app.main import app

from tests.test_utils import create_and_upload_test_pdf


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_pdf_upload(client):

    response = create_and_upload_test_pdf(client)

    assert response.status_code == 200
    assert "pdf_id" in response.json()
