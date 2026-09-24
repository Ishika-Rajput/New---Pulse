# Architecture

RSS sources are ingested by the Python service. Entries are normalized, full article text is extracted where possible, duplicates are skipped, and articles are grouped with TF-IDF/cosine similarity.

The Node.js service exposes cluster and timeline data to the Next.js frontend and triggers ingestion jobs.

The frontend presents clusters as a visual timeline and lets users inspect articles and filter sources.
