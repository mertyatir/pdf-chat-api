from config import logger
from typing import List
import chromadb
from chromadb.api import ClientAPI


def get_or_create_collection(
    client: ClientAPI,
    collection_name: str,
) -> chromadb.Collection:

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
