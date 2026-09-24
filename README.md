# News Pulse

Topic-clustered news timeline built as a full-stack application for the Xponentium India Full-Stack Developer Internship assessment.

News Pulse collects articles from multiple public RSS feeds, extracts article content, removes duplicates, groups related articles into topic clusters using TF-IDF and cosine similarity, stores the results in PostgreSQL, and presents the clusters through an interactive Next.js timeline.

---

## Features

- Fetches news from 3 public RSS feeds:
  - BBC
  - NPR
  - The Guardian
- Handles inconsistent RSS feed fields
- Normalizes article metadata into a common schema
- Extracts article body content from original article pages
- Handles article extraction failures gracefully
- Deduplicates articles using URL-based identifiers
- Topic clustering using TF-IDF and cosine similarity
- Keyword-based automatic cluster labeling
- PostgreSQL persistence using Supabase
- REST API built with Node.js and Express
- Interactive Next.js / React timeline
- Visual timeline showing the temporal span of topic clusters
- Filter timeline by news source
- Click a cluster to view its related articles
- Refresh Data button to trigger a new ingestion job
- Ingestion status polling
- Cross-source topic grouping
- Responsive frontend interface

---

## Architecture

```text
                    ┌─────────────────────┐
                    │   Public RSS Feeds  │
                    │                     │
                    │ BBC / NPR / Guardian │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Python Scraper   │
                    │                     │
                    │ RSS Parser          │
                    │ Normalizer          │
                    │ Article Extractor   │
                    │ Deduplicator        │
                    │ TF-IDF Clustering   │
                    │ Cluster Labeler     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ PostgreSQL /        │
                    │ Supabase            │
                    │                     │
                    │ Articles            │
                    │ Clusters            │
                    │ Cluster Relations   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Node.js + Express   │
                    │ REST API            │
                    │                     │
                    │ Clusters            │
                    │ Timeline            │
                    │ Ingestion           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Next.js / React     │
                    │                     │
                    │ Timeline            │
                    │ Source Filter       │
                    │ Cluster Details     │
                    │ Refresh Data        │
                    └─────────────────────┘

Project Structure
news-pulse/
│
├── scraper/
│   ├── config/
│   │   └── feeds.py
│   │
│   ├── ingestion/
│   │   ├── rss_parser.py
│   │   ├── normalizer.py
│   │   ├── article_extractor.py
│   │   └── deduplicator.py
│   │
│   ├── clustering/
│   │   ├── preprocessor.py
│   │   ├── tfidf_cluster.py
│   │   └── cluster_labeler.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── utils/
│   │   ├── dates.py
│   │   └── logging_config.py
│   │
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .venv/
│
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   └── database.js
│   │   │
│   │   ├── routes/
│   │   │   ├── clusters.routes.js
│   │   │   ├── timeline.routes.js
│   │   │   └── ingestion.routes.js
│   │   │
│   │   └── server.js
│   │
│   ├── package.json
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.js
│   │   ├── layout.js
│   │   ├── globals.css
│   │   └── cluster/
│   │       └── [id]/
│   │           └── page.js
│   │
│   ├── components/
│   │   ├── Timeline.jsx
│   │   ├── TimelineCluster.jsx
│   │   ├── ClusterDetails.jsx
│   │   ├── SourceFilter.jsx
│   │   ├── RefreshButton.jsx
│   │   ├── LoadingState.jsx
│   │   └── ErrorState.jsx
│   │
│   ├── lib/
│   │   ├── api.js
│   │   └── formatters.js
│   │
│   ├── public/
│   ├── package.json
│   └── .env.example
│
├── database/
│
├── docs/
│
├── .github/
│   └── workflows/
│
├── .gitignore
├── docker-compose.yml
├── LICENSE
└── README.md

1. Data Ingestion

The scraper uses three public RSS feeds:

BBC
NPR
The Guardian

Each feed can expose slightly different field names and structures. The ingestion pipeline normalizes these differences into a common article representation.

Normalized article fields

source
headline
summary
rss_content
url
published_at

The article URL is used as the primary deduplication signal.

If the RSS entry does not contain a usable URL, a fallback identifier is generated using available article metadata.

2. Article Content Extraction

RSS feeds do not always contain the complete article body.

For each normalized article, News Pulse attempts to fetch the original article page and extract readable text using trafilatura.

The extraction process is designed to fail gracefully.

If extraction fails:

RSS metadata
     ↓
Article extraction
     ↓
Failure
     ↓
Continue ingestion

One failed article does not stop the complete ingestion process.

3. Deduplication

Articles are deduplicated before being stored.

The preferred identifier is generated from the article URL:

SHA-256(article_url)

If a URL is unavailable, the system falls back to a combination of:

source + headline + published_at

This allows repeated ingestion runs without creating duplicate articles for the same URL.

4. Topic Clustering

Topic clustering is one of the main components of News Pulse.

The system uses:

TF-IDF vectorization
Cosine similarity
Headline keywords
Connected-component style grouping
Text preparation

Article text is cleaned by:

Removing HTML tags
Converting text to lowercase
Removing punctuation
Normalizing whitespace

The clustering representation gives additional weight to article headlines by repeating the headline before the summary.

Conceptually:

headline + headline + headline + summary

This helps the clustering algorithm focus on the main topic of an article.

TF-IDF

The implementation uses:

TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.90
)

Both unigrams and bigrams are considered.

This allows the system to capture expressions such as:

white house
trade war
artificial intelligence
climate change

rather than relying only on individual words.

Similarity

Cosine similarity is calculated between article TF-IDF vectors.

The main similarity threshold is:

0.35

If two articles have a cosine similarity of at least 0.35, they are considered related.

A secondary rule is used for articles that share multiple meaningful keywords:

shared keywords >= 2
AND
cosine similarity >= 0.12

This helps identify related articles where wording differs between news sources.

Generic Keyword Filtering

Very common news words are excluded from keyword-based matching.

Examples include generic terms related to:

news
report
said
says
today
latest
people
government
official
world
year

This reduces accidental clustering caused by common vocabulary rather than actual topics.

Roundup Handling

Roundup-style articles can contain many unrelated stories in one article.

These articles are treated conservatively and are generally kept as singleton clusters instead of being allowed to incorrectly merge unrelated topics.

Cluster Formation

Related articles are grouped into topic clusters.

Each cluster contains:

Cluster ID
Cluster Label
Articles
Article Count
Earliest Published Time
Latest Published Time
Sources

For example:

Cluster
├── Label: White House Media Access
├── Article 1: BBC
├── Article 2: NPR
├── Article 3: Guardian
└── Article 4: BBC

This allows the frontend to show a single topic across multiple news sources.

5. Cluster Labeling

Cluster labels are generated from meaningful keywords appearing in the articles belonging to the cluster.

The labels are intended to provide a concise representation of the topic rather than reproduce an entire headline.

Examples can include labels such as:

White House Media Access
Trump China Relations
Hurricane Polo
Iran President Speech
6. Database

News Pulse uses PostgreSQL hosted through Supabase.

The main database tables are:

articles

Stores normalized and extracted article information.

Important fields:

id
source
headline
summary
content
url
published_at
created_at
clusters

Stores topic cluster information.

Important fields:

id
label
created_at
cluster_articles

Many-to-many relationship between clusters and articles.

cluster_id
article_id
ingestion_jobs

The database schema also contains an ingestion job table for job persistence and future extension.

The current backend implementation tracks active ingestion job status in server memory while the Python scraper is running.

7. Backend API

The backend is implemented using:

Node.js
Express
PostgreSQL

Default local backend URL:

http://localhost:5000
GET /health

Checks whether the backend is running.

Example:

GET /health

Response:

{
  "status": "ok"
}
GET /clusters

Returns the available topic clusters.

Example:

GET /clusters

Example response:

[
  {
    "id": 1,
    "label": "White House Media Access",
    "article_count": 4
  }
]
GET /clusters/:id

Returns a specific cluster and its articles.

Example:

GET /clusters/1

The response contains:

Cluster information
Article headline
Source
Summary
Article URL
Published timestamp
GET /timeline

Returns the data required by the frontend timeline.

Example:

GET /timeline

Each timeline item contains information such as:

id
label
start
end
count
intensity
sources

Example:

{
  "id": 1,
  "label": "White House Media Access",
  "start": "2026-09-24T08:10:00Z",
  "end": "2026-09-24T12:30:00Z",
  "count": 4,
  "intensity": 4,
  "sources": [
    "BBC",
    "NPR"
  ]
}

The start and end timestamps allow the frontend to represent the temporal span of each cluster.

POST /ingest/trigger

Triggers a new ingestion process.

Example:

POST /ingest/trigger

Response:

{
  "jobId": "example-job-id",
  "status": "queued"
}

The backend launches the Python ingestion process asynchronously.

The frontend does not block while ingestion is running.

GET /ingest/status/:jobId

Returns the current status of an ingestion job.

Example:

GET /ingest/status/example-job-id

Possible states include:

queued
running
completed
failed

The frontend polls this endpoint until the job finishes.

8. Frontend

The frontend is built using:

Next.js
React
CSS

Default local frontend URL:

http://localhost:3000
Timeline

The main page displays topic clusters on a horizontal timeline.

Each cluster is positioned based on its publication range:

earliest article
       ↓
    cluster
       ↓
latest article

The visual representation makes it possible to see when a topic appeared and how long articles related to the topic were published.

Cluster Details

Clicking a cluster opens its associated article information.

The details include:

Headline
Source
Publication time
Article URL
Summary

The article link can be opened to visit the original news source.

Source Filter

The frontend provides source filtering for:

All
BBC
NPR
Guardian

Selecting a source filters the displayed timeline to clusters containing articles from that source.

Refresh Data

The Refresh Data button performs the following workflow:

User clicks Refresh Data
        ↓
POST /ingest/trigger
        ↓
Receive job ID
        ↓
Poll /ingest/status/:jobId
        ↓
Wait until completed
        ↓
Fetch updated timeline
        ↓
Update UI

This allows the user to retrieve newly available RSS articles without restarting the application.

9. Environment Variables

Environment variables are used so that database credentials and deployment configuration are not hard-coded into the source code.

Scraper

Create:

scraper/.env

Example:

DATABASE_URL=your_postgresql_connection_string
Backend

Create:

backend/.env

Example:

PORT=5000
DATABASE_URL=your_postgresql_connection_string
Frontend

Create:

frontend/.env.local

Example:

NEXT_PUBLIC_API_URL=http://localhost:5000

For production, this should point to the deployed backend URL.

10. Local Setup
Prerequisites

Install:

Python 3.14+
Node.js
npm
Git
PostgreSQL-compatible database

Supabase can be used as the hosted PostgreSQL database.

11. Setup Python Scraper

Open a terminal in the project root:

cd news-pulse\scraper

Create a virtual environment:

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Create:

scraper/.env

and add:

DATABASE_URL=your_postgresql_connection_string
12. Run the Scraper

From:

news-pulse/scraper

run:

python main.py

A successful run performs:

Fetch RSS feeds
       ↓
Normalize articles
       ↓
Remove duplicates
       ↓
Extract article content
       ↓
Generate TF-IDF vectors
       ↓
Calculate similarities
       ↓
Create clusters
       ↓
Save articles
       ↓
Save clusters

Example output:

Articles fetched: 86
Unique articles: 86
Duplicates removed: 0
Article extraction successful: 86
Clusters generated: 81
Clusters saved: 81
Relationships saved: 86

The exact numbers may vary because RSS feeds change over time.

13. Run the Backend

Open another terminal:

cd news-pulse\backend

Install dependencies:

npm install

Create:

backend/.env

Example:

PORT=5000
DATABASE_URL=your_postgresql_connection_string

Start the backend:

npm start

The API will be available at:

http://localhost:5000

Test:

http://localhost:5000/health
14. Run the Frontend

Open another terminal:

cd news-pulse\frontend

Install dependencies:

npm install

Create:

frontend/.env.local

Example:

NEXT_PUBLIC_API_URL=http://localhost:5000

Start the development server:

npm run dev

Open:

http://localhost:3000
15. Complete Local Workflow

The complete application can be run using three processes.

Terminal 1 — Scraper
cd news-pulse\scraper
.\.venv\Scripts\Activate.ps1
python main.py
Terminal 2 — Backend
cd news-pulse\backend
npm start
Terminal 3 — Frontend
cd news-pulse\frontend
npm run dev

Then open:

http://localhost:3000
16. API Testing

The following endpoints can be tested independently.

Health
GET http://localhost:5000/health
Clusters
GET http://localhost:5000/clusters
Individual cluster
GET http://localhost:5000/clusters/1
Timeline
GET http://localhost:5000/timeline
Trigger ingestion
POST http://localhost:5000/ingest/trigger
Check ingestion
GET http://localhost:5000/ingest/status/<jobId>
17. Error Handling

The application handles failures at multiple levels.

RSS failures

If a feed cannot be fetched, the scraper logs the failure and continues processing the remaining feeds.

Article extraction failures

If an individual article cannot be extracted, the scraper continues processing other articles.

Database failures

Database operations are wrapped with error handling and transactions where appropriate.

API failures

The backend returns HTTP error responses with JSON error messages.

Frontend failures

The frontend displays error states when API requests or ingestion operations fail.

18. Current Clustering Limitation

The clustering system uses text similarity and keyword overlap, so it is sensitive to the wording used by different news sources.

Two articles discussing the same event may use significantly different language and therefore receive a lower similarity score.

Conversely, unrelated articles can occasionally share several generic or event-related terms and be grouped together.

For example, articles involving similar terms such as:

sentenced
years
prison

may occasionally appear more related than they actually are.

The current implementation reduces this risk through:

TF-IDF similarity thresholds
Generic keyword filtering
Headline weighting
Bigram features
Conservative handling of roundup articles

However, semantic embeddings or a more advanced topic-modeling approach could improve clustering quality further.

19. Possible Future Improvements

Potential improvements include:

Replace TF-IDF with transformer-based semantic embeddings
Use a vector database for large-scale similarity search
Improve cluster labeling using an LLM
Add automatic periodic ingestion
Persist ingestion job status directly in PostgreSQL
Add authentication and API rate limiting
Add richer cluster visualizations
Add cluster-size-based visual scaling
Improve cross-source event detection
Add historical clustering instead of rebuilding clusters on every ingestion
Add automated tests and CI/CD checks
Add monitoring and structured logging
20. Security Considerations

Sensitive credentials should never be committed to Git.

The following files should remain local:

scraper/.env
backend/.env
frontend/.env.local

Only example environment files should be committed:

.env.example

Database credentials should be stored using deployment platform environment variables in production.

21. Deployment

The application is designed to be deployable as three logical components:

Frontend
   ↓
Next.js hosting platform

Backend
   ↓
Node.js hosting platform

Database
   ↓
Supabase PostgreSQL

Python ingestion
   ↓
Python-capable deployment environment

Recommended deployment architecture:

                ┌──────────────────┐
                │   Next.js App    │
                │    Frontend      │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Node + Express   │
                │     Backend      │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │    Supabase      │
                │   PostgreSQL     │
                └────────┬─────────┘
                         ▲
                         │
                ┌────────┴─────────┐
                │ Python Scraper   │
                │ RSS + Clustering │
                └──────────────────┘
Production environment variables

Frontend:

NEXT_PUBLIC_API_URL=<deployed-backend-url>

Backend:

PORT=<platform-provided-port>
DATABASE_URL=<supabase-postgresql-url>

Scraper:

DATABASE_URL=<supabase-postgresql-url>
Live Deployment URLs
Frontend
TODO: Add deployed frontend URL
Backend
TODO: Add deployed backend URL
Health Endpoint
TODO: Add deployed backend /health URL
22. Assessment Demo Flow

A recommended demonstration flow is:

1. Open the deployed frontend

Show the News Pulse timeline.

2. Explain the timeline

Point out:

Topic clusters
Publication time span
Article count
Source information
3. Use source filtering

Select:

BBC
NPR
Guardian

and show how the timeline changes.

4. Open a cluster

Click a cluster and demonstrate:

Related headlines
Sources
Publication timestamps
Original article links
5. Refresh the data

Click:

Refresh Data

Explain that the frontend:

POST /ingest/trigger
        ↓
polls job status
        ↓
waits for completion
        ↓
reloads timeline
6. Explain clustering

Briefly explain:

RSS
 ↓
Normalization
 ↓
Article extraction
 ↓
Deduplication
 ↓
TF-IDF
 ↓
Cosine similarity
 ↓
Topic clusters
7. Discuss one limitation

Explain that lexical similarity can miss semantically related articles when different sources use different wording.

23. Technology Stack
Frontend
Next.js
React
JavaScript
CSS
Backend
Node.js
Express
PostgreSQL client (pg)
Scraper / Data Processing
Python
feedparser
Requests
BeautifulSoup
Trafilatura
python-dateutil
scikit-learn
python-dotenv
Database
PostgreSQL
Supabase
Machine Learning / NLP
TF-IDF
Cosine Similarity
Keyword-based cluster labeling
24. Key Design Decisions
Why RSS?

RSS provides a simple, public and structured way to collect articles from multiple news sources without requiring a custom scraper for every website.

Why article extraction?

RSS feeds may contain only headlines and short summaries. Fetching the original article allows the system to obtain additional text for processing.

Why TF-IDF?

TF-IDF is lightweight, explainable, fast to implement, and suitable for a small-to-medium collection of news articles.

Why cosine similarity?

Cosine similarity provides a straightforward way to measure similarity between TF-IDF document vectors.

Why PostgreSQL?

The application has relational data:

Articles
Clusters
Cluster ↔ Article relationships

PostgreSQL provides a natural relational model for this structure.

Why Next.js?

Next.js provides a convenient React-based framework for building the interactive timeline frontend.

25. Development Notes

The scraper can be run independently from the backend.

This makes it possible to:

Develop/test ingestion
        ↓
Store results in PostgreSQL
        ↓
Develop/test API
        ↓
Develop/test frontend

The backend can also trigger the scraper through the ingestion endpoint.