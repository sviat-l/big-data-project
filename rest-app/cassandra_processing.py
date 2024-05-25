import cassandra_client

host, port, keyspace = 'cassandra', 9042, 'wiki'
connection = cassandra_client.CassandraClient(host, port, keyspace)
connection.connect()


def find_all_domains():
    query = f"SELECT DISTINCT domain FROM {keyspace}.domain_pages;"
    rows = connection.session.execute(query)
    return {"domains": [str(row.domain) for row in rows]}


def find_user_pages(user_id):
    query = f"SELECT * FROM {keyspace}.user_pages WHERE user_id = {user_id};"
    rows = connection.session.execute(query)
    return [{"page_id": row.page_id, "page_title": row.page_title} for row in rows]


def find_page_info(page_id):
    query = f"SELECT * FROM {keyspace}.pages WHERE page_id = {page_id};"
    row = connection.session.execute(query).one()
    return {"page_id": row.page_id, "page_title": row.page_title, "domain": row.domain}


def find_domain_pages(domain):
    query = f"SELECT COUNT(*) FROM {keyspace}.domain_pages WHERE domain = %s"
    row = connection.session.execute(query, [domain]).one()
    return {"number_of_pages": row.count}


def find_pages_by_users_in_timerange(from_dt, to_dt):
    querry = f"SELECT user_id, user_text, COUNT(page_id) as count FROM {keyspace}.pages_by_date \
    WHERE created_at >= '{from_dt}' AND created_at <= '{to_dt}' \
    GROUP BY created_at ALLOW FILTERING;"
    result = connection.session.execute(querry).all()
    return [{"user_id": row.user_id, "user_name": row.user_text, "number_of_pages": row.count} for row in result]


def fetch_domain_page_counts():
    query = "SELECT domain, COUNT(*) AS count FROM {keyspace}.pages GROUP BY domain"
    rows = connection.session.execute(query)
    return {row.domain: row.count for row in rows}


def fetch_bot_creation_stats():
    query = "SELECT domain, COUNT(*) AS count FROM {keyspace}.domain_stats WHERE user_is_bot = True ALLOW FILTERING"
    rows = connection.session.execute(query)
    return {row.domain: row.count for row in rows}


def fetch_top_users():
    query = """
    SELECT user_id, COUNT(*) AS count, COLLECT_SET(page_title) AS page_titles
    FROM {keyspace}.user_pages
    GROUP BY user_id
    ORDER BY count DESC
    LIMIT 20;
    """
    rows = connection.session.execute(query)
    return [{"user_id": row.user_id, "number_of_pages": row.count, "page_titles": list(row.page_titles)} for row in rows]
