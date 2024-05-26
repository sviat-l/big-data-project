from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import List, Dict
import logging


# Initialize logging
logging.basicConfig(level=logging.INFO, format='|%(asctime)s| - |%(name)s| - |%(levelname)s| - |%(message)s|')
logger = logging.getLogger(__name__)

# Initialize MongoDB client
MONGO_URL = 'mongodb://mongodb:27017'
DB_NAME = 'wikiData'


class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.setup_indexes()

    def setup_indexes(self):
        self.db.domain_stats.create_index([("time_start", 1)])
        self.db.bot_creation_stats.create_index([("time_start", 1)])
        self.db.most_productive.create_index([("time_start", 1)])

    def insert_domain_stats(self, domain_counts):
        try:
            self.db.domain_stats.delete_many({})
            self.db.domain_stats.insert_one(domain_counts)
            logger.info("Domain stats inserted successfully.")
        except Exception as e:
            logger.error(f"Failed to insert domain stats: {str(e)}")

    def insert_bot_creation_stats(self, bot_stats):
        try:
            self.db.bot_creation_stats.delete_many({})
            self.db.bot_creation_stats.insert_one(bot_stats)
            logger.info("Bot creation stats inserted successfully.")
        except Exception as e:
            logger.error(f"Failed to insert bot creation stats: {str(e)}")

    def insert_most_productive(self, top_users):
        try:
            self.db.most_productive.delete_many({})
            self.db.most_productive.insert_one(top_users)
            logger.info("Most productive users stats inserted successfully.")
        except Exception as e:
            logger.error(f"Failed to insert top users stats: {str(e)}")

    def get_domain_stats(self) -> List[Dict]:
        try:
            data = list(self.db.domain_stats.find())
            return data
        except Exception as e:
            logging.error(f"Failed to fetch hourly domain stats: {str(e)}")
            return []

    def get_bot_creation_stats(self) -> Dict:
        try:
            data = list(self.db.bot_creation_stats.find())
            return data if data else {}
        except Exception as e:
            logging.error(f"Failed to fetch bot creation stats: {str(e)}")
            return {}

    def get_most_productive(self) -> List[Dict]:
        try:
            data = list(self.db.most_productive.find())
            return data
        except Exception as e:
            logging.error(f"Failed to fetch top users: {str(e)}")
            return []
