import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

google_api_key = os.getenv("GEMINI_API_KEY")


set_llm_cache(SQLiteCache(database_path=".langchain.db"))


"""
langchain uses pydantic v1 and SecretStr type is not compatible
with pydantic v2
 """
llm = ChatGoogleGenerativeAI(
    model="gemini-pro", api_key=google_api_key  # type: ignore
)


llm.max_output_tokens = 8196
