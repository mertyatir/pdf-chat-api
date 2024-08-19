from fastapi import HTTPException
from models.chat_models import MessageRequest


def validate_pdf_id(pdf_id: str):
    if not pdf_id:
        raise HTTPException(
            status_code=400,
            detail="PDF ID cannot be empty.",
        )


def validate_message(message: MessageRequest):
    user_message = message.message
    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )
    return user_message
