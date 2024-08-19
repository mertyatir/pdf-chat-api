from fastapi import HTTPException
from models import PDFFile
from sqlalchemy.orm import Session


def get_pdf_file(pdf_id: str, db: Session) -> PDFFile:
    pdf_file = db.query(PDFFile).filter(PDFFile.id == pdf_id).first()

    if not pdf_file:
        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    return pdf_file
