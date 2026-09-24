from collections import Counter
import re

STOP_WORDS = {
    "about",
    "after",
    "again",
    "also",
    "been",
    "being",
    "could",
    "from",
    "have",
    "into",
    "more",
    "other",
    "said",
    "their",
    "there",
    "these",
    "they",
    "this",
    "those",
    "what",
    "when",
    "where",
    "which",
    "while",
    "will",
    "with",
    "would",
}


def label_cluster(articles: list[dict]) -> str:
    """
    Generate a simple human-readable label from
    the most common meaningful headline words.
    """

    words = []

    for article in articles:
        headline = article.get("headline", "")

        extracted = re.findall(
            r"[A-Za-z]{4,}",
            headline.lower(),
        )

        words.extend(
            word
            for word in extracted
            if word not in STOP_WORDS
        )

    common_words = Counter(words).most_common(3)

    if not common_words:
        return "General News"

    return " / ".join(
        word.title()
        for word, _ in common_words
    )