import cassandra_client
import logging
import os
from datetime import datetime, timedelta

# Initialize logging
logging.basicConfig(level=logging.INFO, format='|%(asctime)s| - |%(name)s| - |%(levelname)s| - |%(message)s|')
logger = logging.getLogger(__name__)

class CassandraService:
    def __init__(self, host=None, port=None, keyspace=None):
        self.host = os.getenv("CASSANDRA_HOST", "cassandra") if host is None else host
        self.port = os.getenv("CASSANDRA_PORT", 9042) if port is None else port
        self.keyspace = os.getenv("CASSANDRA_KEYSPACE", "wiki") if keyspace is None else keyspace
        self.cassandra = None
        self.connect_to_db()
        logger.info(f"CassandraService initialized with host: {self.host}, port: {self.port}, keyspace: {self.keyspace}")

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
        querry = f""" SELECT user_id, user_text, COUNT(page_id) as count
            FROM {self.keyspace}.pages_by_date
            WHERE created_at >= '{from_dt}' AND created_at <= '{to_dt}'
            GROUP BY created_at ALLOW FILTERING"""
        results = self.cassandra.execute(querry).all()
        return [{"user_id": row.user_id, "user_name": row.user_text, "number_of_pages": row.count} for row in results]

    def fetch_domain_page_counts(self):
        current_time = datetime.utcnow()
        from_time = current_time - timedelta(hours=7)
        to_time = current_time - timedelta(hours=1)
        from_time = from_time.strftime("%Y-%m-%dT%H:00")
        to_time = to_time.strftime("%Y-%m-%dT%H:00")
        query = f"""
        SELECT domain, created_at, COUNT(*) AS count \
        FROM {self.keyspace}.domain_stats \
        WHERE created_at >= '{from_time}' AND created_at < '{to_time}' \
        GROUP BY domain ALLOW FILTERING;
        """
        rows = self.cassandra.execute(query).all()
        hourly_results = {}
        for row in rows:
            hour = datetime.strptime(row.created_at, "%Y-%m-%dT%H:%M:%SZ")
            next_hour = (hour + timedelta(hours=1))
            if hour not in hourly_results:
                hourly_results[hour] = {}
                hourly_results[hour]["time_start"] = hour.strftime("%Y-%m-%dT%H:00")
                hourly_results[hour]["time_end"] = next_hour.strftime("%Y-%m-%dT%H:00")
                hourly_results[hour]["statistics"] = []
            hourly_results[hour]["statistics"].append({"domain": row.domain, "created_pages": row.count})    
        return {"data": list(hourly_results.values())}

    def fetch_bot_creation_stats(self):
        current_time = datetime.utcnow()
        from_time = current_time - timedelta(hours=7)
        to_time = current_time - timedelta(hours=1)
        from_time = from_time.strftime("%Y-%m-%dT%H:00")
        to_time = to_time.strftime("%Y-%m-%dT%H:00")
        query = f"""
        SELECT domain, COUNT(*) AS count \
        FROM {self.keyspace}.domain_stats \
        WHERE user_is_bot = True \
        AND created_at >= '{from_time}' AND created_at < '{to_time}' \
        GROUP BY domain ALLOW FILTERING;
        """
        rows = self.cassandra.execute(query)
        return {
            "time_start": from_time,
            "time_end": to_time,
            "statistics": [{"domain": row.domain, "created_by_bots": row.count} for row in rows]
        }

    def fetch_top_users(self, limit=20):
        current_time = datetime.utcnow()
        from_time = current_time - timedelta(hours=7)
        to_time = current_time - timedelta(hours=1)
        from_time = from_time.strftime("%Y-%m-%dT%H:00")
        to_time = to_time.strftime("%Y-%m-%dT%H:00")
        query = f"""
        SELECT * FROM {self.keyspace}.pages_by_date
        WHERE created_at >= '{from_time}' AND created_at < '{to_time}'
        ALLOW FILTERING ;
        """
        rows = self.cassandra.execute(query).all()
        users = {}
        for row in rows:
            user = row.user_id
            if user not in users:
                users[user] = {"total_pages":0, "page_titles":[], "user_name":row.user_text, "user_id":row.user_id}
            page = row.page_title
            users[user]["total_pages"] += 1
            users[user]["page_titles"].append(page)
            
        top_users = sorted(list(users.values()), key=lambda x: -x['total_pages'])[:limit]
        return {
            "time_start": from_time,
            "time_end": to_time,
            "users": top_users
        }
