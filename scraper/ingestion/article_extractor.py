import trafilatura


def extract_article(url: str) -> str | None:
    """
    Extract the main article body from a URL.

    Returns None if the page cannot be downloaded or parsed.
    A failed article must not stop the complete ingestion run.
    """

    if not url:
        return None

    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return None

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )

        if not text:
            return None

        return text.strip()

    except Exception as error:
        print(f"[WARNING] Article extraction failed: {url}")
        print(f"          Reason: {error}")
        return None