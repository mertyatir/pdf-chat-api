from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column
from config import logger
from utils.pdf_utils import validate_pdf
import uuid
import pypdf
from pypdf.errors import PdfStreamError
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

    try:
        file_content = await file.read()

        pdf_reader = pypdf.PdfReader(file.file)
        page_count = len(pdf_reader.pages)

        # Store the PDF file in the database
        pdf_file = PDFFile(
            id=pdf_id,
            filename=file.filename,
            content=file_content,
            page_count=page_count,
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

    except PdfStreamError as e:
        logger.error("Failed to read PDF file: %s", e)
        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to read PDF file. The file may be corrupted",
                "or improperly formatted.",
            ),
        )
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred while",
                "processing the PDF file.",
            ),
        )
