from fastapi import APIRouter, UploadFile, Depends
import hashlib

from config import logger
from config.database import get_db

from validators.validate_pdf import validate_pdf
from utils import extract_text_from_pdf, split_text, preprocess_text

from models.pdf_models import UploadPDFResponse

from services.chromaDB import (
    get_or_create_collection,
    populate_collection,
)
from services.pdf_service import get_pdf_file_from_file_hash, store_pdf_file

from sqlalchemy.ext.asyncio import AsyncSession


pdf_router = APIRouter()


@pdf_router.post(
    "/",
    response_model=UploadPDFResponse,
)
async def upload_pdf(
    file: UploadFile,
    session: AsyncSession = Depends(get_db),
):

    await validate_pdf(file)
    logger.info("Uploading PDF file: %s", file.filename)

    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    existing_file = await get_pdf_file_from_file_hash(file_hash, session)

    if existing_file:
        return {
            "pdf_id": existing_file.id,
        }

    pdf_id = await store_pdf_file(file, file_content, file_hash, session)

    extracted_text = extract_text_from_pdf(file.file)
    cleaned_text = preprocess_text(extracted_text)
    chunked_text = split_text(cleaned_text)

    collection = get_or_create_collection(pdf_id)

    populate_collection(collection, chunked_text)

    logger.info("PDF file uploaded successfully: %s", file.filename)
    return {
        "pdf_id": pdf_id,
    }
