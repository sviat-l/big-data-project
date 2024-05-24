CREATE KEYSPACE IF NOT EXISTS wiki WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};


CREATE TABLE IF NOT EXISTS wiki.domain_pages (
    domain TEXT,
    page_id INT,
    PRIMARY KEY (domain, page_id),
);

CREATE TABLE IF NOT EXISTS wiki.user_pages (
    user_id INT,
    page_id INT,
    page_title TEXT,
    PRIMARY KEY (user_id, page_id),
);

CREATE TABLE IF NOT EXISTS wiki.pages (
    page_id INT,
    page_title TEXT,
    domain TEXT,
    PRIMARY KEY (page_id, domain),
);

CREATE TABLE IF NOT EXISTS wiki.pages_by_date (
    created_at TEXT,
    page_id INT,
    page_title TEXT,
    user_id INT,
    user_text TEXT,
    domain TEXT,
    PRIMARY KEY (created_at, page_id),
);


CREATE TABLE IF NOT EXISTS wiki.domain_stats (
    created_at TEXT,
    domain TEXT,
    page_id INT,
    user_is_bot BOOLEAN,
    PRIMARY KEY ((created_at, user_is_bot), domain)
);
