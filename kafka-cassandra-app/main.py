import csv
import argparse
from kafka import KafkaConsumer
import cassandra_models
from kafka.consumer.fetcher import ConsumerRecord
from abstract_cassandra_db import CassandraDB


def write_to_database(casandra_db: CassandraDB, message: dict[str]):
    """ Write a message to the Cassandra DB"""
    casandra_db.insert_into_db(message)


def get_transaction_info_from_message(message: ConsumerRecord) -> dict[str]:
    """ Collect the transaction information from a Kafka message """
    fields = ('step', 'type', 'amount', 'name_orig', 'oldbalance_orig', 'newbalance_orig',
              'name_dest', 'oldbalance_dest', 'newbalance_dest', 'is_fraud', 'is_flagged_fraud', 
              'transaction_date', 'transaction_id')
    reader = csv.DictReader([message.value],
                            fieldnames=fields,
                            )
    message_dict = next(reader)
    return message_dict


def process_messages(kafka_consumer: KafkaConsumer, db: CassandraDB, log_every: int=-1, limit: int=-1):
    """ Process messages from a Kafka consumer and write to a Cassandra DB"""
    n_written = 0
    for message in kafka_consumer:
        message_dict = get_transaction_info_from_message(message)
        write_to_database(db, message_dict)
        n_written += 1
        if log_every > 0 and n_written % log_every == 0:
            print(f"Processed {n_written} messages")
        if not limit or n_written == limit:
            break
    return n_written

def connect_to_kafka(topic: str, bootstrap_servers: str) -> KafkaConsumer:
    """ Connect to a Kafka server and return a KafkaConsumer object"""
    kafka_consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_servers,
                                   value_deserializer=lambda x: x.decode('utf-8'))
    if not kafka_consumer.bootstrap_connected():
        print(f"Could not connect to Kafka server: {bootstrap_servers}. Please retry.")
        exit(1)
    print(f"Connected to Kafka server: {bootstrap_servers} and topic: {topic}")
    return kafka_consumer

def connect_to_cassandra(host: str, port: int, keyspace: str) -> CassandraDB:
    """ Connect to Cassandra and return a CassandraDB object"""
    transactions_DB = CassandraDB(host, port, keyspace)
    transactions_DB.add_tables([cassandra_models.TransactionsByDate, cassandra_models.ClientTransactions])
    transactions_DB.connect()
    print(f"CONNECTED TO CASSANDRA with HOST: {host}, PORT: {port}, KEYSPACE: {keyspace}")
    return transactions_DB
    
def main(args: argparse.Namespace):
    """
    Main function to connect to Kafka and Cassandra.
    Process messages from Kafka and write to Cassandra
    """
    kafka_consumer = connect_to_kafka(args.topic, args.bootstrap_servers)
    transactions_DB = connect_to_cassandra(args.host, args.port, args.keyspace)
    num_messages_writen = process_messages(kafka_consumer, transactions_DB, args.log_every, args.limit)
    print(f"In total processed {num_messages_writen} messages")
    kafka_consumer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Read messages from Kafka topic and write to Cassandra DB.')
    parser.add_argument('--bootstrap-servers', type=str,
                        default="kafka-server:9092", help='Kafka bootstrap servers')
    parser.add_argument('--topic', type=str, default="transactions",
                        help='Kafka topic name to read messages from')
    parser.add_argument('--host', type=str, default="cassandra",
                        help='Cassandra host')
    parser.add_argument('--port', type=int, default=9042, help='Cassandra port')
    parser.add_argument('--keyspace', type=str, default="transactions",
                        help='Cassandra keyspace')
    parser.add_argument('--log_every', type=int,
                        default=5000, help='Log every n messages processed')
    parser.add_argument("--limit", type=int, default=-1, help="Limit the number of messages to process")
    args = parser.parse_args()
    main(args)
