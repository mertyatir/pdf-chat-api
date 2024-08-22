import os
from config import logger
from typing import List
import chromadb
from chromadb import QueryResult


persist_directory = os.path.join(os.getcwd(), "chroma_db")
client = chromadb.PersistentClient(path=persist_directory)


# TODO: Use async vector database instead of ChromaDB


def get_or_create_collection(
    pdf_id: str,
) -> chromadb.Collection:

    collection_name = pdf_id

    collection = client.get_or_create_collection(name=collection_name)

    return collection


def populate_collection(
    collection: chromadb.Collection,
    chunked_text: List[str],
):

    for idx, chunk in enumerate(chunked_text):
        collection.add(
            documents=[chunk],
            ids=[f"id_{idx}"],
        )
        logger.info("Knowledge base is being indexed to ChromaDb.")
    logger.info("Collection populated successfully.")


def query_collection(
    collection: chromadb.Collection,
    user_message: str,
    n_results: int,
) -> QueryResult:

    results = collection.query(
        query_texts=[user_message],
        n_results=n_results,
    )
    logger.info("Results: %s", results.get("documents"))
    return results
