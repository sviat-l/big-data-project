from cassandra_processing import *
import datetime

def process_data_to_mongo():
    cassandra = AdHocCassandraService()
    mongo_client = MongoDBClient()
    
    domain_counts = cassandra.fetch_domain_page_counts()
    bot_stats = cassandra.fetch_bot_creation_stats()
    top_users = cassandra.fetch_top_users()

    mongo_client.insert_domain_stats(domain_counts)
    mongo_client.insert_bot_creation_stats(bot_stats)
    mongo_client.insert_most_productive(top_users)

    print("Data processed and loaded to MongoDB")

if __name__ == "__main__":
    process_data_to_mongo()
