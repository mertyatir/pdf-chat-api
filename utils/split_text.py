from typing import List


from semantic_text_splitter import TextSplitter

"""
Using the `semantic_text_splitter` library instead of
`langchain.semantic_text_splitter`
because the latter does not support setting a maximum chunk size.
This limitation causes
exceeding the context size of the model.
"""


def split_text(text: str) -> List[str]:
    """
    Split the text based on semantic similarity.

    :param text: The original text to split.
    :return: A list of text chunks.
    """

    max_characters = 1000
    splitter = TextSplitter(max_characters)
    chunks = splitter.chunks(text)

    return chunks
