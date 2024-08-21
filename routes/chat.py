from fastapi import APIRouter, Path, Body, Depends

from config import logger, get_or_create_chat_history
from config.database import get_db

from models.chat_models import MessageRequest, ChatResponse

from utils import (
    generate_response_with_gemini,
)

from services.pdf_service import get_pdf_file
from services.chromaDB import get_or_create_collection, query_collection

from validators.chat_with_pdf import (
    validate_message,
)

from sqlalchemy.ext.asyncio import AsyncSession

chat_router = APIRouter()


@chat_router.post("/{pdf_id}/", response_model=ChatResponse)
async def chat_with_pdf(
    pdf_id: str = Path(..., description="The ID of the PDF file"),
    message: MessageRequest = Body(...),
    session: AsyncSession = Depends(get_db),
):

    logger.info("Chatting with PDF: %s", pdf_id)
    logger.info("Message: %s", message.message)

    pdf_file = await get_pdf_file(pdf_id, session)

    user_message = validate_message(message)

    collection = get_or_create_collection(pdf_id)

    results = query_collection(
        collection,
        user_message,
        n_results=5,
    )

    if results["documents"]:
        concatenated_documents = "".join(results["documents"][0])
    else:
        concatenated_documents = ""

    chat_history = await get_or_create_chat_history(pdf_file.session_id)
    conversation_history = await chat_history.aget_messages()

    logger.info("conversation_history: %s", conversation_history)
    response = await generate_response_with_gemini(
        user_message,
        concatenated_documents,
        conversation_history,
        chat_history,
    )
    return {"response": response}
