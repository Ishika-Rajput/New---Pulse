import os
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

from config.feeds import FEEDS
from ingestion.rss_parser import fetch_feed
from ingestion.normalizer import normalize_entry
from ingestion.article_extractor import extract_article
from ingestion.deduplicator import generate_article_id

from clustering.tfidf_cluster import cluster_articles
from clustering.cluster_labeler import label_cluster

from database.repository import (
    insert_article,
    create_cluster,
    add_article_to_cluster,
)

from database.connection import get_connection


load_dotenv()


def main():

    print("=" * 60)
    print("NEWS PULSE - FULL INGESTION PIPELINE")
    print("=" * 60)

    articles = []
    seen_ids = set()

    total_fetched = 0
    extraction_success = 0
    extraction_failed = 0
    duplicates = 0
    old_articles_skipped = 0

    # ---------------------------------------------------------
    # 1. FETCH RSS FEEDS
    # ---------------------------------------------------------

    for source, url in FEEDS.items():

        print(f"\nFetching {source}...")

        raw_articles = fetch_feed(source, url)

        total_fetched += len(raw_articles)

        for item in raw_articles:

            article = normalize_entry(
                item["raw"],
                item["source"]
            )

            article_id = generate_article_id(article)

            # -------------------------------------------------
            # Remove duplicate articles
            # -------------------------------------------------

            if article_id in seen_ids:
                duplicates += 1
                continue

            seen_ids.add(article_id)

            article["id"] = article_id

            # -------------------------------------------------
            # Ignore articles older than 30 days
            # -------------------------------------------------

            if article["published_at"]:

                try:

                    published_time = datetime.fromisoformat(
                        article["published_at"].replace(
                            "Z",
                            "+00:00"
                        )
                    )

                    cutoff_time = (
                        datetime.now(timezone.utc)
                        - timedelta(days=30)
                    )

                    if published_time < cutoff_time:

                        old_articles_skipped += 1

                        print(
                            f"[SKIP] Old article: "
                            f"{article['headline'][:80]}"
                        )

                        continue

                except (
                    ValueError,
                    TypeError,
                    OverflowError
                ):

                    print(
                        f"[WARNING] Invalid publication date: "
                        f"{article['headline'][:80]}"
                    )

            # -------------------------------------------------
            # 2. EXTRACT ARTICLE CONTENT
            # -------------------------------------------------

            print(
                f"Extracting: "
                f"{article['headline'][:80]}"
            )

            content = extract_article(
                article["url"]
            )

            if content:

                article["content"] = content
                extraction_success += 1

            else:

                article["content"] = ""
                extraction_failed += 1

            articles.append(article)

    # ---------------------------------------------------------
    # 3. INGESTION SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)

    print(
        f"Articles fetched:       "
        f"{total_fetched}"
    )

    print(
        f"Unique articles:        "
        f"{len(articles)}"
    )

    print(
        f"Duplicate articles:     "
        f"{duplicates}"
    )

    print(
        f"Old articles skipped:   "
        f"{old_articles_skipped}"
    )

    print(
        f"Extraction successful:  "
        f"{extraction_success}"
    )

    print(
        f"Extraction failed:      "
        f"{extraction_failed}"
    )

    # ---------------------------------------------------------
    # 4. SAVE ARTICLES TO POSTGRESQL
    # ---------------------------------------------------------

    print(
        "\nSaving articles to PostgreSQL..."
    )

    inserted = 0

    try:

        with get_connection() as connection:

            for article in articles:

                try:

                    insert_article(
                        connection,
                        article
                    )

                    inserted += 1

                except Exception as error:

                    print(
                        f"[ERROR] Could not save article: "
                        f"{article['headline'][:60]}"
                    )

                    print(
                        f"        {error}"
                    )

            connection.commit()

        print(
            f"[OK] Articles processed for database: "
            f"{inserted}"
        )

    except Exception as error:

        print(
            "[ERROR] PostgreSQL operation failed"
        )

        print(error)

    # ---------------------------------------------------------
    # 5. RUN TOPIC CLUSTERING
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("RUNNING TOPIC CLUSTERING")
    print("=" * 60)

    clusters = cluster_articles(
        articles
    )

    print(
        f"Clusters generated: "
        f"{len(clusters)}"
    )

    # ---------------------------------------------------------
    # 6. SAVE CLUSTERS TO POSTGRESQL
    # ---------------------------------------------------------

    print(
        "\nSaving clusters to PostgreSQL..."
    )

    clusters_saved = 0
    cluster_articles_saved = 0

    try:

        with get_connection() as connection:

            # Rebuild clusters on every ingestion run.
            # Article data is preserved; only cluster
            # assignments are replaced.

            with connection.cursor() as cursor:

                cursor.execute(
                    "DELETE FROM cluster_articles;"
                )

                cursor.execute(
                    "DELETE FROM clusters;"
                )

            # -------------------------------------------------
            # Create new clusters
            # -------------------------------------------------

            for number, cluster_indexes in enumerate(
                clusters,
                start=1
            ):

                cluster_articles_data = [
                    articles[index]
                    for index in cluster_indexes
                ]

                label = label_cluster(
                    cluster_articles_data
                )

                cluster_id = create_cluster(
                    connection,
                    label
                )

                clusters_saved += 1

                # -------------------------------------------------
                # Create article-cluster relationships
                # -------------------------------------------------

                for article in cluster_articles_data:

                    add_article_to_cluster(
                        connection,
                        cluster_id,
                        article["id"]
                    )

                    cluster_articles_saved += 1

                print(
                    f"Cluster {number}: "
                    f"{label} "
                    f"({len(cluster_articles_data)} articles)"
                )

            connection.commit()

        print(
            f"\n[OK] Clusters saved: "
            f"{clusters_saved}"
        )

        print(
            f"[OK] Cluster-article relationships saved: "
            f"{cluster_articles_saved}"
        )

    except Exception as error:

        print(
            "[ERROR] Could not save clusters"
        )

        print(error)

        # Make the process fail so the backend
        # correctly reports the ingestion job as failed.
        raise

    # ---------------------------------------------------------
    # 7. COMPLETE
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("NEWS PULSE INGESTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()