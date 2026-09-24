from database.connection import get_connection

from database.connection import get_connection


def insert_article(connection, article: dict) -> None:
    query = """
        INSERT INTO articles (
            id,
            source,
            headline,
            summary,
            content,
            url,
            published_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url)
        DO UPDATE SET
            source = EXCLUDED.source,
            headline = EXCLUDED.headline,
            summary = EXCLUDED.summary,
            content = EXCLUDED.content,
            published_at = EXCLUDED.published_at;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                article["id"],
                article["source"],
                article["headline"],
                article.get("summary") or "",
                article.get("content") or "",
                article["url"],
                article.get("published_at"),
            ),
        )


def create_cluster(connection, label: str) -> int:
    query = """
        INSERT INTO clusters (label)
        VALUES (%s)
        RETURNING id;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (label,))
        result = cursor.fetchone()

    return result[0]


def add_article_to_cluster(
    connection,
    cluster_id: int,
    article_id: str
) -> None:

    query = """
        INSERT INTO cluster_articles (
            cluster_id,
            article_id
        )
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                cluster_id,
                article_id
            ),
        )


def get_article_count() -> int:
    query = "SELECT COUNT(*) FROM articles;"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

    return result[0]

def insert_article(connection, article: dict) -> None:
    query = """
        INSERT INTO articles (
            id,
            source,
            headline,
            summary,
            content,
            url,
            published_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url)
        DO UPDATE SET
            source = EXCLUDED.source,
            headline = EXCLUDED.headline,
            summary = EXCLUDED.summary,
            content = EXCLUDED.content,
            published_at = EXCLUDED.published_at;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                article["id"],
                article["source"],
                article["headline"],
                article.get("summary") or "",
                article.get("content") or "",
                article["url"],
                article.get("published_at"),
            ),
        )


def get_article_count() -> int:
    query = "SELECT COUNT(*) FROM articles;"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

    return result[0]