from db.cassandra_processing import CassandraService
from db.mongo_processing import MongoDBClient
import datetime
import time
import logging

logging.basicConfig(level=logging.INFO, format='|%(asctime)s| - |%(name)s| - |%(levelname)s| - |%(message)s|')
logger = logging.getLogger(__name__)

def process_data_to_mongo():
    cassandra = CassandraService()
    mongo_client = MongoDBClient()
    
    domain_counts = cassandra.fetch_domain_page_counts()
    bot_stats = cassandra.fetch_bot_creation_stats()
    top_users = cassandra.fetch_top_users()
    
    logger.info("Data fetched from Cassandra")

    mongo_client.insert_domain_stats(domain_counts)
    mongo_client.insert_bot_creation_stats(bot_stats)
    mongo_client.insert_most_productive(top_users)

    logger.info("Data processed and loaded to MongoDB")

    
def wait_loop():
    previous_hour = datetime.datetime.now().hour
    while True:
        current_hour = datetime.datetime.now().hour
        if current_hour == previous_hour:
            logger.info("Waiting for the next hour to process data,"\
                        f" current  {current_hour}, previous hour: {previous_hour}")
            time.sleep(10)
            continue
        logger.info("New hour, processing data for precomputed reports")
        process_data_to_mongo()
        previous_hour = current_hour
            

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run the batch processing once and exit")
    args = parser.parse_args()
    
    if args.once:
        process_data_to_mongo()
    else:
        wait_loop()
