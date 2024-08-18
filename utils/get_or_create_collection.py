from fastapi import HTTPException
from config import logger
from typing import List
import chromadb


def get_or_create_collection(
    client,
    collection_name: str,
    embedding_function,
    chunked_text: List[str],
) -> chromadb.Collection:

    collection = None
    try:
        collection = client.get_collection(
            name=collection_name, embedding_function=embedding_function
        )
        if not collection:
            logger.info(
                "Collection not found. Creating and populating collection."
            )
            populate_collection(
                client, collection_name, embedding_function, chunked_text
            )
        else:

            logger.info("Collection found.")
    except Exception as e:
        logger.error("Error getting collection: %s", e)
        populate_collection(
            client, collection_name, embedding_function, chunked_text
        )

    if not collection:
        raise HTTPException(
            status_code=500,
            detail=(
                "Collection could not be created or"
                + " retrieved successfully.",
            ),
        )
    return collection


def populate_collection(
    client, collection_name, embedding_function, chunked_text
):

    try:
        collection = client.create_collection(
            name=collection_name,
            embedding_function=embedding_function,
        )
        for idx, chunk in enumerate(chunked_text):
            collection.add(
                documents=[chunk],
                ids=[f"id_{idx}"],
            )
            logger.info("Knowledge base is being indexed to ChromaDb.")
        logger.info("Collection populated successfully.")
    except Exception as e:
        logger.error("Error populating collection: %s", e)
