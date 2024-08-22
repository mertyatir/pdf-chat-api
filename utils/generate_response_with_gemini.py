from config import llm, logger
from typing import List
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from fastapi import HTTPException
from langchain_postgres import PostgresChatMessageHistory
from langchain.prompts import PromptTemplate


async def generate_response_with_gemini(
    user_message: str,
    extracted_text: str,
    conversation_history: List[BaseMessage],
    chat_history: PostgresChatMessageHistory,
) -> BaseMessage:

    try:

        template = """
        Based on the following PDF content: {extracted_text}\n\n
        Conversation history: {conversation_history}\n
        User's question: {user_message}
        """

        prompt = PromptTemplate.from_template(template)

        chain = prompt | llm

        response = chain.invoke(
            {
                "user_message": user_message,
                "conversation_history": conversation_history,
                "extracted_text": extracted_text,
            }
        )

        await chat_history.aadd_messages(
            [
                HumanMessage(content=user_message),
                AIMessage(content=response.content),
            ]
        )
        logger.info("Response generated: %s", response.content)
        return response

    except Exception as e:
        logger.error("An error occurred while generating response: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the response.",
        )
