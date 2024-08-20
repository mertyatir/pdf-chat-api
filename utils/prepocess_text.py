import re
import spacy
import logging


# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def preprocess_text(text: str) -> str:

    logging.info("Preprocessing text...")
    # Remove duplicate spaces and newline characters
    text = re.sub(r"\s+", " ", text)

    # Remove page numbers, headers, and footers
    # (example: remove lines with only digits)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)

    # Split text into sentences using spaCy
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    # Join sentences back into a single string
    cleaned_text = " ".join(sentences)

    return cleaned_text
