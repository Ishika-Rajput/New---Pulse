import feedparser
import requests


def fetch_feed(source: str, url: str) -> list[dict]:
    """
    Fetch and parse an RSS feed.

    A failure in one source should not stop the complete
    ingestion process.
    """
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "NewsPulse/1.0"
            },
        )
        response.raise_for_status()

        parsed = feedparser.parse(response.content)

        if not parsed.entries:
            print(f"[WARNING] {source}: no articles found")
            return []

        articles = []

        for entry in parsed.entries:
            articles.append({
                "source": source,
                "raw": entry,
            })

        print(f"[OK] {source}: {len(articles)} articles found")

        return articles

    except requests.RequestException as error:
        print(f"[ERROR] {source}: {error}")
        return []

    except Exception as error:
        print(f"[ERROR] {source}: unexpected error - {error}")
        return []