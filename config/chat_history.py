import uuid
from langchain_postgres import PostgresChatMessageHistory
import psycopg


table_name = "chat_history"
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/pdf_chat_db"


async def bootstrap_db():
    await create_chat_history_table()


async def create_chat_history_table():

    async_connection = await psycopg.AsyncConnection.connect(DATABASE_URL)
    # Create the table schema (only needs to be done once)
    await PostgresChatMessageHistory.acreate_tables(
        async_connection, table_name
    )


async def get_or_create_chat_history(session_id=None):
    if session_id is None:
        session_id = str(uuid.uuid4())

    async_connection = await psycopg.AsyncConnection.connect(DATABASE_URL)

    # Initialize the chat history manager
    chat_history = PostgresChatMessageHistory(
        table_name, session_id, async_connection=async_connection
    )

    return chat_history
