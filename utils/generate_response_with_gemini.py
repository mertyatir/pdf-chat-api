from config import model, logger, chat_history
from typing import List
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from fastapi import HTTPException


def generate_response_with_gemini(
    user_message: str,
    extracted_text: str,
    conversation_history: List[BaseMessage],
) -> str:

    try:
        response = model.generate_content(
            f"Based on the following PDF content: {extracted_text}\n\n"
            f"Conversation history: {conversation_history}\n"
            f"User's question: {user_message}"
        )

        chat_history.add_messages(
            [
                HumanMessage(content=user_message),
                AIMessage(content=response.text),
            ]
        )
        logger.info("Response generated: %s", response.text)
        return response.text

    except Exception as e:
        logger.error("An error occurred while generating response: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the response.",
        )
