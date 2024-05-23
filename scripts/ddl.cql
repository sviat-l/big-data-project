CREATE KEYSPACE IF NOT EXISTS wiki WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS wiki.created_pages (
    request_id UUID, 
    user_id BIGINT,
    domain TEXT,
    created_at TIMESTAMP,
    page_title TEXT,
    PRIMARY KEY ((request_id), created_at, domain, page_title)
) WITH CLUSTERING ORDER BY (created_at DESC);
