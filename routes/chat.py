from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy import Column
from sqlalchemy.orm import Session
from config import logger, get_or_create_chat_history
from models.chat_models import MessageRequest, ChatResponse
from utils import (
    generate_response_with_gemini,
)
from services.chromaDB import (
    get_or_create_collection,
)
import os
import chromadb
from db.get_db import get_db
from services.pdf_service import get_pdf_file
from validators.chat_with_pdf import (
    validate_message,
)


chat_router = APIRouter()


@chat_router.post("/{pdf_id}/", response_model=ChatResponse)
async def chat_with_pdf(
    pdf_id: str = Path(..., description="The ID of the PDF file"),
    message: MessageRequest = Body(...),
    db: Session = Depends(get_db),  # Dependency injection
):

    logger.info("Chatting with PDF: %s", pdf_id)
    logger.info("Message: %s", message.message)

    pdf_file = get_pdf_file(pdf_id, db)

    pdf_content = pdf_file.content
    if not isinstance(pdf_content, bytes):
        raise HTTPException(
            status_code=500,
            detail="PDF content is not in binary format.",
        )

    user_message = validate_message(message)

    persist_directory = os.path.join(os.getcwd(), "persist")
    client = chromadb.PersistentClient(path=persist_directory)

    collection_name = pdf_file.id

    if isinstance(collection_name, Column):
        collection_name = collection_name.value

    collection = get_or_create_collection(client, collection_name)

    # Query the collection
    results = collection.query(
        query_texts=[user_message],
        n_results=5,
        # Increase the number to get more accurate
        # results for the summarization
    )

    logger.info("Results: %s", results.get("documents"))

    if results["documents"]:
        concatenated_documents = "".join(results["documents"][0])
    else:
        concatenated_documents = ""

    chat_history = get_or_create_chat_history(pdf_file.session_id)
    conversation_history = chat_history.messages

    logger.info("conversation_history: %s", conversation_history)
    response = generate_response_with_gemini(
        user_message,
        concatenated_documents,
        conversation_history,
        chat_history,
    )
    return {"response": response}
