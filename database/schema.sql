CREATE TABLE IF NOT EXISTS clusters (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER REFERENCES clusters(id) ON DELETE SET NULL,
    source TEXT NOT NULL,
    headline TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT NOT NULL UNIQUE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_articles_cluster_id
    ON articles(cluster_id);

CREATE INDEX IF NOT EXISTS idx_articles_published_at
    ON articles(published_at);
