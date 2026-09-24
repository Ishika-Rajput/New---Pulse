import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessor import clean_text


# A higher threshold prevents unrelated news stories
# from being connected merely because their summaries
# contain similar general news language.
TFIDF_THRESHOLD = 0.35

GENERIC_WORDS = {
    "this", "that", "with", "from", "have", "after", "before",
    "into", "about", "their", "they", "were", "been", "being",
    "what", "when", "where", "which", "while", "than", "over",
    "under", "more", "also", "just", "could", "should", "would",
    "will", "said", "says", "tell", "tells", "amid", "among",
    "during", "through", "against", "between",

    # Generic news vocabulary
    "news", "live", "latest", "story", "stories", "report",
    "reports", "reported", "according", "people", "person",
    "year", "years", "time", "times", "moment", "world",
    "country", "countries", "official", "officials",
    "leader", "leaders", "government", "president",
    "administration", "minister", "ministers",

    # Generic verbs
    "make", "makes", "made", "take", "takes", "took",
    "gets", "get", "got", "goes", "went", "come", "comes",
    "came", "saying", "calls", "called", "looks", "looking",
    "seen", "find", "finds", "found", "shows", "show",
    "shown", "gives", "give", "gave", "faces", "face",

    # Generic descriptive words
    "new", "big", "major", "first", "second", "third",
    "least", "long", "high", "early", "late", "rare",
    "possible", "likely", "right", "good", "best"
}


def extract_keywords(article):
    """
    Extract meaningful words from the headline.
    Headline keywords are given much more importance than
    generic summary vocabulary.
    """

    headline = article.get("headline", "").lower()

    words = re.findall(r"[a-zA-Z]{4,}", headline)

    return {
        word
        for word in words
        if word not in GENERIC_WORDS
    }


def extract_phrases(article):
    """
    Extract two-word phrases from the headline.

    Example:
        "Hurricane Polo intensifies"

    produces:
        hurricane polo
        polo intensifies
    """

    headline = article.get("headline", "").lower()

    words = re.findall(r"[a-zA-Z]{4,}", headline)

    words = [
        word
        for word in words
        if word not in GENERIC_WORDS
    ]

    phrases = set()

    for i in range(len(words) - 1):
        phrases.add(f"{words[i]} {words[i + 1]}")

    return phrases


def keyword_overlap(first_keywords, second_keywords):
    """
    Number of meaningful headline keywords shared
    by two articles.
    """

    return len(first_keywords & second_keywords)


def has_strong_shared_phrase(first_phrases, second_phrases):
    """
    Exact meaningful phrase appearing in both headlines.
    """

    return len(first_phrases & second_phrases) > 0


def articles_are_related(
    tfidf_score,
    shared_keywords,
    shared_phrase
):
    """
    Conservative topic matching.

    A topic connection requires either:
    - strong textual similarity, or
    - multiple meaningful headline keywords.

    A shared generic phrase alone is not sufficient.
    """

    # Strong similarity
    if tfidf_score >= 0.35:
        return True

    # Multiple meaningful headline terms
    if shared_keywords >= 2 and tfidf_score >= 0.12:
        return True

    return False

def is_roundup_article(article):
    headline = article.get("headline", "").lower()

    roundup_terms = [
        "the papers",
        "as it happened",
        "news live",
        "live:",
        "live -",
        "live news"
    ]

    return any(term in headline for term in roundup_terms)

def cluster_articles(articles):
    """
    Group related news articles using:

    - TF-IDF cosine similarity
    - headline keyword overlap
    - exact headline phrase overlap

    Headline text is intentionally repeated to give it
    more weight than the summary.
    """

    if not articles:
        return []
    
    roundup_indexes = {
    index
    for index, article in enumerate(articles)
    if is_roundup_article(article)
}

    documents = []

    for article in articles:

        headline = article.get("headline", "")
        summary = article.get("summary", "")

        # Give headline considerably more importance
        # than summary.
        text = (
            f"{headline} "
            f"{headline} "
            f"{headline} "
            f"{summary}"
        )

        documents.append(clean_text(text))

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.90
    )

    matrix = vectorizer.fit_transform(documents)

    similarity_matrix = cosine_similarity(matrix)

    keyword_sets = [
        extract_keywords(article)
        for article in articles
    ]

    phrase_sets = [
        extract_phrases(article)
        for article in articles
    ]

    visited = set()
    clusters = []

    for index in range(len(articles)):

        if index in visited:
            continue

        # Keep roundup/live articles separate.
        # These articles can mention multiple unrelated stories.
        if index in roundup_indexes:
            visited.add(index)
            clusters.append([index])
            continue

        cluster = []
        queue = [index]

        visited.add(index)

        while queue:

            current = queue.pop(0)

            cluster.append(current)

            for candidate in range(len(articles)):

                if candidate in visited:
                    continue

                # Do not merge roundup/live articles
                # into normal topic clusters.
                if candidate in roundup_indexes:
                    continue

                tfidf_score = similarity_matrix[current][candidate]

                shared_keywords = keyword_overlap(
                    keyword_sets[current],
                    keyword_sets[candidate]
                )

                shared_phrase = has_strong_shared_phrase(
                    phrase_sets[current],
                    phrase_sets[candidate]
                )

                if articles_are_related(
                    tfidf_score,
                    shared_keywords,
                    shared_phrase
                ):
                    visited.add(candidate)
                    queue.append(candidate)

        clusters.append(sorted(cluster))

    return clusters