from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy import Column
from sqlalchemy.orm import Session
from config import logger, chat_history, google_api_key
from models import PDFFile
from models.chat_models import MessageRequest, ChatResponse

from utils import (
    extract_text_from_pdf,
    split_text,
    generate_response_with_gemini,
    get_or_create_collection,
)
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from db.get_db import get_db


chat_router = APIRouter()


@chat_router.post("/{pdf_id}/", response_model=ChatResponse)
async def chat_with_pdf(
    pdf_id: str = Path(...),
    message: MessageRequest = Body(...),
    db: Session = Depends(get_db),  # Dependency injection
):
    if not pdf_id:
        raise HTTPException(
            status_code=400,
            detail="PDF ID cannot be empty.",
        )

    logger.info("Chatting with PDF: %s", pdf_id)
    logger.info("Message: %s", message.message)

    pdf_file = db.query(PDFFile).filter(PDFFile.id == pdf_id).first()

    if not pdf_file:
        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    pdf_content = pdf_file.content
    if not isinstance(pdf_content, bytes):
        raise HTTPException(
            status_code=500,
            detail="PDF content is not in binary format.",
        )

    user_message = message.message
    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    extracted_text = extract_text_from_pdf(pdf_content)
    logger.info("Extracted text: %s", extracted_text)

    persist_directory = os.path.join(os.getcwd(), "persist")
    collection_name = pdf_file.filename

    if isinstance(collection_name, Column):
        collection_name = collection_name.value

    client = chromadb.PersistentClient(path=persist_directory)

    # create embedding function
    embedding_function = (
        embedding_functions.GoogleGenerativeAiEmbeddingFunction  # type: ignore
    )(api_key=google_api_key, task_type="RETRIEVAL_QUERY")

    # Check if the collection exists and populate if necessary
    chunked_text = split_text(extracted_text)
    collection = get_or_create_collection(
        client, collection_name, embedding_function, chunked_text
    )

    # Query the collection to get the 5 most relevant results
    results = collection.query(
        query_texts=[user_message],
        n_results=5,
    )
    if results["documents"]:
        concatenated_documents = " ".join(results["documents"][0])
    else:
        concatenated_documents = ""

    logger.info("Concatenated documents: %s", concatenated_documents)

    conversation_history = chat_history.messages
    response = generate_response_with_gemini(
        user_message, concatenated_documents, conversation_history
    )
    return {"response": response}
