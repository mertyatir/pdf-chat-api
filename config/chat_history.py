import psycopg
import uuid
from langchain_postgres import PostgresChatMessageHistory
from config import DATABASE_URL

sync_connection = psycopg.connect(DATABASE_URL)


table_name = "chat_history"

"""
# Create the table schema (only needs to be done once)

PostgresChatMessageHistory.create_tables(sync_connection, table_name)
"""

session_id = str(uuid.uuid4())

# Initialize the chat history manager
chat_history = PostgresChatMessageHistory(
    table_name, session_id, sync_connection=sync_connection
)
