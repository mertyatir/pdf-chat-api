from fastapi import HTTPException, UploadFile

import pypdf
import uuid

from models import PDFFile

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_pdf_file(pdf_id: str, session: AsyncSession) -> PDFFile:
    q = select(PDFFile).filter(PDFFile.id == pdf_id)
    pdf_file = await session.execute(q)
    pdf_file = pdf_file.scalars().first()

    if not pdf_file:
        raise HTTPException(
            status_code=404,
            detail="PDF not found in the database.",
        )

    return pdf_file


async def get_pdf_file_from_file_hash(
    file_hash: str, session: AsyncSession
) -> PDFFile:

    q = select(PDFFile).filter(PDFFile.file_hash == file_hash)
    result = await session.execute(q)
    existing_file = result.scalars().first()

    return existing_file


async def store_pdf_file(
    file: UploadFile,
    file_content: bytes,
    file_hash: str,
    session: AsyncSession,
) -> str:
    pdf_id = str(uuid.uuid4())
    pdf_reader = pypdf.PdfReader(file.file)
    page_count = len(pdf_reader.pages)
    session_id = str(uuid.uuid4())
    pdf_file = PDFFile(
        id=pdf_id,
        filename=file.filename,
        content=file_content,
        page_count=page_count,
        file_hash=file_hash,
        session_id=session_id,
    )
    session.add(pdf_file)

    return pdf_id
