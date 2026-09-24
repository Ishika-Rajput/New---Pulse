from config.feeds import FEEDS
from ingestion.rss_parser import fetch_feed
from ingestion.normalizer import normalize_entry
from clustering.tfidf_cluster import cluster_articles
from clustering.cluster_labeler import label_cluster


def main():

    print("=" * 60)
    print("NEWS PULSE - TOPIC CLUSTERING TEST")
    print("=" * 60)

    articles = []

    for source, url in FEEDS.items():

        raw_articles = fetch_feed(source, url)

        for item in raw_articles:

            article = normalize_entry(
                item["raw"],
                item["source"]
            )

            articles.append(article)

    print(
        f"\nArticles available for clustering: "
        f"{len(articles)}"
    )

    clusters = cluster_articles(articles)

    print(
        f"Clusters generated: {len(clusters)}"
    )

    print("\n" + "=" * 60)
    print("CLUSTER RESULTS")
    print("=" * 60)

    for number, cluster_indexes in enumerate(
        clusters,
        start=1
    ):

        cluster_data = [
            articles[index]
            for index in cluster_indexes
        ]

        label = label_cluster(cluster_data)

        print(
            f"\nCluster {number}: {label}"
        )

        print(
            f"Articles: {len(cluster_data)}"
        )

        for article in cluster_data[:10]:

            print(
                f"  - [{article['source']}] "
                f"{article['headline']}"
            )

        if len(cluster_data) > 10:

            print(
                f"  ... and "
                f"{len(cluster_data) - 10} more"
            )


if __name__ == "__main__":
    main()