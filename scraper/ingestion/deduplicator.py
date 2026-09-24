import hashlib


def generate_article_id(article: dict) -> str:
    """
    Generate a stable unique identifier for an article.

    The article URL is preferred because it is normally unique.
    If a URL is unavailable, we fall back to source + headline
    + publication timestamp.
    """

    unique_value = article.get("url")

    if not unique_value:
        unique_value = (
            f"{article.get('source', '')}|"
            f"{article.get('headline', '')}|"
            f"{article.get('published_at', '')}"
        )

    return hashlib.sha256(
        unique_value.encode("utf-8")
    ).hexdigest()