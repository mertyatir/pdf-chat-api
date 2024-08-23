import pytest

from config import llm

from config.logger import logger

from langchain.prompts import PromptTemplate


@pytest.mark.asyncio
async def test_gemini_integration():

    user_message = "What is the capital of France?"
    extracted_text = "Paris is the capital of France."
    conversation_history = [
        "Hello, how can I help you?",
        "I am looking for information about France.",
    ]

    template = """
    Based on the following PDF content: {extracted_text}\n\n
    Conversation history: {conversation_history}\n
    User's question: {user_message}
    """

    prompt = PromptTemplate.from_template(template)

    chain = prompt | llm

    response = await chain.ainvoke(
        {
            "user_message": user_message,
            "conversation_history": conversation_history,
            "extracted_text": extracted_text,
        }
    )
    logger.info(f"Response: {response}")
    assert response.content is not None
