from kafka import KafkaProducer
import requests
import argparse
import time
import logging

logging.basicConfig(level=logging.INFO, format='|%(asctime)s| - |%(name)s| - |%(levelname)s| - |%(message)s|')
logger = logging.getLogger(__name__)

def send_to_kafka(kafka_producer:KafkaProducer, topic:str, message: str) -> None:
    """ Send the messsage to the Kafka topic"""
    kafka_producer.send(topic, message.encode())

    
def produce_from_stream(endponint_path:str, kafka_producer:KafkaProducer, topic:str, log_every:int, post_limit:int) -> int:
    """ Produce message from the stream by endpoint path to the Kafka topic"""
    num_posted_messages = 0
    finish_execution = False
    while not finish_execution:
        response = requests.get(endponint_path, stream=True)
        logger.info(f"Connected to the stream from {endponint_path} with status code: {response.status_code}")
        try:
            for line in response.iter_lines():
                line = line.decode('utf-8')
                send_to_kafka(kafka_producer, topic, line)
                num_posted_messages += 1
                if log_every and num_posted_messages % log_every == 0:
                    logger.info(f"Posted {num_posted_messages} messages to Kafka")
                if post_limit > 0 and num_posted_messages >= post_limit:
                    finish_execution = True
                    break
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            logger.info("Trying to reconnect to the stream...")
    return num_posted_messages

def main(args:argparse.Namespace):
    endponint_path = args.endponint_path
    bootstrap_servers = args.bootstrap_servers
    topic = args.topic
    log_every = args.log_every
    post_limit = args.post_limit
    
    start = time.time()
    logger.info("Starting the Kafka producer...")
    kafka_producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    logger.info(f"Connected to Kafka producer with bootstrap servers: {bootstrap_servers}, {kafka_producer.bootstrap_connected()}")
    logger.info(f"Reading stream messages from {endponint_path} ...")
    num_posted_messages = produce_from_stream(endponint_path, kafka_producer, topic, log_every, post_limit)

    kafka_producer.flush()
    kafka_producer.close()
    logger.info("Kafka producer closed.")
    logger.info("Time taken: %s seconds", time.time()-start)
    logger.info("Number of messages posted: %s", num_posted_messages)
    return

if __name__ == "__main__":
    import os
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                        description="Read messages from the stream and write to Kafka topic")
    argparser.add_argument("--endponint_path", type=str, default="https://stream.wikimedia.org/v2/stream/page-create",
                                help="Endpoint path to get the stream of the wiki pages")
    argparser.add_argument("--bootstrap_servers", type=str, default=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
                                help="Kafka server address")
    argparser.add_argument("--topic", type=str, default=os.getenv("KAFKA_TOPIC"),
                                help="Kafka topic name to write to")
    argparser.add_argument("--log_every", type=int, default=1000, help="Log every N messages posted")
    argparser.add_argument("--post_limit", type=int, default=-1, help="Limit the number of messages to post (-1 to post all)")
    args = argparser.parse_args()
    main(args)
