from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column
from config import logger
from utils.pdf_utils import validate_pdf
import uuid
import pypdf
from models import PDFFile
from models.pdf_models import UploadPDFResponse
from db.get_db import get_db
import chromadb
import os
from utils import extract_text_from_pdf, split_text, preprocess_text
from services.chromaDB import (
    get_or_create_collection,
    populate_collection,
)
from services.pdf_service import get_pdf_file
import hashlib


pdf_router = APIRouter()


@pdf_router.post(
    "/",
    response_model=UploadPDFResponse,
)
async def upload_pdf(
    file: UploadFile,
    db: Session = Depends(get_db),
):

    await validate_pdf(file)

    logger.info("Uploading PDF file: %s", file.filename)

    pdf_id = str(uuid.uuid4())

    file_content = await file.read()

    # Compute the hash of the file content
    file_hash = hashlib.sha256(file_content).hexdigest()

    # Check if the hash already exists in the database
    existing_file = db.query(PDFFile).filter_by(file_hash=file_hash).first()
    if existing_file:
        return {
            "pdf_id": existing_file.id,
        }

    pdf_reader = pypdf.PdfReader(file.file)
    page_count = len(pdf_reader.pages)

    session_id = str(uuid.uuid4())

    # Store the PDF file in the database
    pdf_file = PDFFile(
        id=pdf_id,
        filename=file.filename,
        content=file_content,
        page_count=page_count,
        file_hash=file_hash,
        session_id=session_id,
    )
    db.add(pdf_file)
    db.commit()

    collection_name = pdf_file.filename

    if isinstance(collection_name, Column):
        collection_name = collection_name.value

    pdf_file = get_pdf_file(pdf_id, db)
    collection_name = pdf_file.filename
    if isinstance(collection_name, Column):
        collection_name = collection_name.value

    pdf_content = pdf_file.content
    if not isinstance(pdf_content, bytes):
        raise HTTPException(
            status_code=500,
            detail="PDF content is not in binary format.",
        )

    extracted_text = extract_text_from_pdf(pdf_content)
    cleaned_text = preprocess_text(extracted_text)
    chunked_text = split_text(cleaned_text)

    persist_directory = os.path.join(os.getcwd(), "persist")
    client = chromadb.PersistentClient(path=persist_directory)
    collection = get_or_create_collection(client, collection_name)

    populate_collection(collection, chunked_text)

    logger.info("PDF file uploaded successfully: %s", file.filename)
    return {
        "pdf_id": pdf_id,
    }
