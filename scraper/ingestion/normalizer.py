from dateutil import parser as date_parser


def parse_published_date(entry):
    """
    Extract and normalize the publication date from an RSS entry.
    Different feeds may use different field names/formats.
    """
    date_value = (
        entry.get("published")
        or entry.get("updated")
        or entry.get("pubDate")
        or entry.get("date")
    )

    if not date_value:
        return None

    try:
        return date_parser.parse(date_value).isoformat()
    except (ValueError, TypeError, OverflowError):
        return None


def extract_summary(entry):
    """
    RSS feeds may provide summaries under different fields.
    """
    return (
        entry.get("summary")
        or entry.get("description")
        or ""
    ).strip()


def extract_content(entry):
    """
    Some RSS feeds expose article content through content:encoded.
    """
    content = entry.get("content")

    if isinstance(content, list) and content:
        return (content[0].get("value") or "").strip()

    return ""


def normalize_entry(entry, source):
    """
    Convert a raw RSS entry into one consistent News Pulse schema.
    """

    return {
        "source": source,
        "headline": (entry.get("title") or "").strip(),
        "summary": extract_summary(entry),
        "rss_content": extract_content(entry),
        "url": (entry.get("link") or "").strip(),
        "published_at": parse_published_date(entry),
    }