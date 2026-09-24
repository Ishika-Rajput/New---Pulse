import re


def clean_text(text: str) -> str:
    """
    Basic text cleaning before TF-IDF.

    Removes HTML, punctuation, and excessive whitespace.
    """
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()