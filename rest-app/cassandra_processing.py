import cassandra_client
import logging
import os

# Initialize logging
logging.basicConfig(level=logging.INFO, format='|%(asctime)s| - |%(name)s| - |%(levelname)s| - |%(message)s|')
logger = logging.getLogger(__name__)

class AdHocCassandraService:
    def __init__(self, host=None, port=None, keyspace=None):
        self.host = os.getenv("CASSANDRA_HOST", "cassandra") if host is None else host
        self.port = os.getenv("CASSANDRA_PORT", 9042) if port is None else port
        self.keyspace = os.getenv("CASSANDRA_KEYSPACE", "wiki") if keyspace is None else keyspace
        self.cassandra = None
        self.connect_to_db()
        logger.info(f"AdHocCassandraService initialized with host: {self.host}, port: {self.port}, keyspace: {self.keyspace}")

    def connect_to_db(self):
        self.cassandra = cassandra_client.CassandraClient(
            self.host, self.port, self.keyspace)
        logger.info(f"Connected to Cassandra at {self.host}:{self.port} with keyspace {self.keyspace}")
        self.cassandra.connect()

    def find_all_domains(self):
        query = f"SELECT DISTINCT domain FROM {self.keyspace}.domain_pages;"
        results = self.cassandra.execute(query)
        return {"domains": [str(row.domain) for row in results]}

    def find_user_pages(self, user_id):
        query = f"SELECT * FROM {self.keyspace}.user_pages WHERE user_id = {user_id};"
        results = self.cassandra.execute(query)
        return [{"page_id": row.page_id, "page_title": row.page_title} for row in results]

    def find_page_info(self, page_id):
        query = f"SELECT * FROM {self.keyspace}.pages WHERE page_id = {page_id};"
        result = self.cassandra.execute(query).one()
        return {"page_id": result.page_id, "page_title": result.page_title, "domain": result.domain}

    def find_domain_pages(self, domain):
        query = f"SELECT COUNT(*) \
            FROM {self.keyspace}.domain_pages\
            WHERE domain = %s"
        result = self.cassandra.execute(query, [domain]).one()
        return {"domain": domain, "number_of_pages": result.count}

    def find_pages_by_users_in_timerange(self, from_dt, to_dt):
        querry = f"SELECT user_id, user_text, COUNT(page_id) as count \
            FROM {self.keyspace}.pages_by_date \
            WHERE created_at >= '{from_dt}' AND created_at <= '{to_dt}' \
            GROUP BY created_at ALLOW FILTERING"
        results = self.cassandra.execute(querry).all()
        return [{"user_id": row.user_id, "user_name": row.user_text, "number_of_pages": row.count} for row in results]


    def fetch_domain_page_counts(self):
        query = "SELECT domain, COUNT(*) AS count FROM {keyspace}.pages GROUP BY domain"
        rows = self.cassandra.execute(query)
        return {row.domain: row.count for row in rows}

    def fetch_bot_creation_stats(self):
        query = "SELECT domain, COUNT(*) AS count FROM {keyspace}.domain_stats WHERE user_is_bot = True ALLOW FILTERING"
        rows = self.cassandra.execute(query)
        return {row.domain: row.count for row in rows}

    def fetch_top_users(self):
        query = """
        SELECT user_id, COUNT(*) AS count, COLLECT_SET(page_title) AS page_titles
        FROM {keyspace}.user_pages
        GROUP BY user_id
        ORDER BY count DESC
        LIMIT 20;
        """
        rows = self.cassandra.execute(query)
        return [{"user_id": row.user_id, "number_of_pages": row.count, "page_titles": list(row.page_titles)} for row in rows]
