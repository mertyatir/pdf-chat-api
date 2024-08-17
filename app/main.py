import logging
from fastapi import FastAPI, UploadFile, HTTPException, Path, Body
import google.generativeai as genai
import os
import uuid
import pypdf
from pypdf.errors import PdfStreamError
from typing import Dict


app = FastAPI()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# In-memory storage for PDFs
pdf_storage = {}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
    ],
)

logger = logging.getLogger(__name__)


async def validate_pdf(file: UploadFile):
    # Validate file type
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed.",
        )

    # Validate file content type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Only PDF files are allowed.",
        )

    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File size exceeds the limit of "
                f"{MAX_FILE_SIZE / (1024 * 1024)} MB."
            ),
        )


@app.post("/v1/pdf")
async def upload_pdf(file: UploadFile):

    await validate_pdf(file)

    logger.info("Uploading PDF file: %s", file.filename)

    pdf_id = str(uuid.uuid4())

    try:

        file_content = await file.read()
        file.file.seek(0)  # Reset file pointer to the beginning

        pdf_reader = pypdf.PdfReader(file.file)
        page_count = len(pdf_reader.pages)

        # Store the PDF file in memory
        pdf_storage[pdf_id] = {
            "content": file_content,
            "metadata": {
                "filename": file.filename,
                "document_id": pdf_id,
                "page_count": page_count,
            },
        }

        logger.info("PDF storage: %s", pdf_storage)

        return {"pdf_id": pdf_id}

    except PdfStreamError as e:
        logger.error("Failed to read PDF file: %s", e)
        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to read PDF file. The file may be corrupted or "
                "improperly formatted."
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


@app.post("/v1/chat/{pdf_id}")
async def chat_with_pdf(
    pdf_id: str = Path(..., description="The ID of the PDF"),
    message: Dict[str, str] = Body(...),
):
    if pdf_id not in pdf_storage:
        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    pdf_data = pdf_storage[pdf_id]
    extracted_text = pdf_data["metadata"]["extracted_text"]

    user_message = message.get("message", "")
    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        response = model.generate_content(
            f"Based on the following PDF content: {extracted_text}\n\n"
            f"User's question: {user_message}"
        )
        return {"response": response.text}

    except Exception as e:
        logger.error("An error occurred while generating response: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the response.",
        )
