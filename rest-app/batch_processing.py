from cassandra_processing import *
import datetime
import pymongo

mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
db = mongo_client['wikiData']

def process_data_to_mongo():
    cassandra = AdHocCassandraService()
    domain_counts = cassandra.fetch_domain_page_counts()
    bot_stats = cassandra.fetch_bot_creation_stats()
    top_users = cassandra.fetch_top_users()

    # Assuming these are dictionaries or lists as needed
    db.domain_stats.insert_one({"data": domain_counts})
    db.bot_creation_stats.insert_one({"data": bot_stats})
    db.most_productive.insert_one({"data": top_users})

    print("Data processed and loaded to MongoDB")

if __name__ == "__main__":
    process_data_to_mongo()
