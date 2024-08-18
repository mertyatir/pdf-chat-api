from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from config import logger
from utils.pdf_utils import validate_pdf
import uuid
import pypdf
from pypdf.errors import PdfStreamError
from models import PDFFile
from db.get_db import get_db

pdf_router = APIRouter()


@pdf_router.post("/")
async def upload_pdf(file: UploadFile, db: Session = Depends(get_db)):

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
