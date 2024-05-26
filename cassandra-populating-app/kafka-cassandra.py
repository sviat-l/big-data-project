import argparse
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.streaming import StreamingQuery
import pyspark.sql.functions as F
from config import CASSANDRA_TABLES

def create_spark_session(app_name: str, master: str, log_level: str, 
                         cassandra_host: str="cassandra", cassandra_port: str="9042"
                         ) -> SparkSession:
    """ Creating the Spark session with the given configurations."""
    spark_session = SparkSession \
            .builder \
            .appName(app_name) \
            .config("spark.streaming.stopGracefullyOnShutdown", True) \
            .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0'+
                                           ',com.datastax.spark:spark-cassandra-connector_2.12:3.1.0') \
            .config("spark.sql.shuffle.partitions", 4) \
            .config("spark.cassandra.connection.host", cassandra_host) \
            .config("spark.cassandra.connection.port", cassandra_port) \
            .master(master) \
            .getOrCreate()
    spark_session.sparkContext.setLogLevel(log_level)
    return spark_session

def read_kafka_stream(spark: SparkSession, bootstrap_servers: str, topic: str) -> DataFrame:
    """ Read messages from Kafka topic as a stream."""
    return spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_servers) \
            .option("subscribe", topic) \
            .load()
            
def append_to_cassandra_table(df: DataFrame, keyspace: str, table: str):
    """ Write data to a Cassandra table."""
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(table=table,keyspace=keyspace
        ).mode("append").save()
            
def write_all_to_cassandra(df: DataFrame, df_id:DataFrame, keyspace: str='wiki'):
    """ Write data to all tables in the keyspace."""
    for table, config in CASSANDRA_TABLES.items():
        batch_df = df.select(config["columns"])
        batch_df = batch_df.filter(batch_df.columns[0] + " IS NOT NULL")
        append_to_cassandra_table(batch_df, keyspace, table)
    
def start_cassandra_write(df: DataFrame) -> StreamingQuery:
    """ Start writing the data to Cassandra."""
    return df.writeStream \
        .foreachBatch(write_all_to_cassandra) \
        .start()

def preprocess_data(input_df: DataFrame) -> DataFrame:
    """ Process the input data and return in the format to write to Cassandra."""
    # Selecting the data from the input stream message
    filtered_df = input_df\
        .selectExpr("CAST(value AS STRING)")\
        .filter(F.expr("value LIKE 'data: %'"))\
        .select(F.expr("substring(value, 7) AS data"))
    # Parsing the JSON data BASED on the data schema
    data_df = filtered_df\
        .selectExpr("from_json(data, 'struct<"+
            "meta:struct<domain:string, request_id:string>, "+
            "performer:struct<user_text:string, user_is_bot:boolean, user_id:integer>, "+
            "dt:string, "+
            "page_id:integer,"
            "page_title:string>') AS data")\
        .select("data.*")
    # Formatting to the proper schema to write to Cassandra
    parsed_df = data_df.select(
        F.col("meta.domain").alias("domain"),
        F.col("meta.request_id").alias("request_id"),
        F.col("performer.user_id").alias("user_id"),
        F.col("performer.user_text").alias("user_text"),
        F.col("performer.user_is_bot").alias("user_is_bot"),
        F.col("dt").alias("created_at"),
        F.col("page_title"),
        F.col("page_id"),
    )
    parsed_df = parsed_df.dropna()
    return parsed_df


def main(args: argparse.Namespace):
    """ Read messages from Kafka topic, filter them, and write to another Kafka topic.
    Args:
    args.boostrap_servers: Kafka bootstrap servers
    args.read_topic: Kafka topic name to read messages from
    args.master: Spark master URL
    args.app_name: Name of the Spark application
    args.log_level: Log level for the Spark context
    args.cassandra_host: Cassandra host
    args.cassandra_port: Cassandra port
    args.keyspace: Cassandra keyspace write to
    """
    spark_session = create_spark_session(args.app_name, args.master, args.log_level, 
                    args.cassandra_host, args.cassandra_port)
    print("Reading from Kafka topic: ", args.read_topic)
    input_df = read_kafka_stream(spark_session, args.bootstrap_servers, args.read_topic)
    processed_df = preprocess_data(input_df)
    print("Writing to Cassandra keyspace", f"{args.keyspace}")
    print("Output Schema:")
    processed_df.printSchema()
    write_query = start_cassandra_write(processed_df)
    write_query.awaitTermination()
    
if __name__ == "__main__":
    import os    
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Read messages from Kafka topic and write to Cassandra.')
    argparser.add_argument('--bootstrap-servers', type=str,
                            default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
                            help='Kafka bootstrap servers')
    argparser.add_argument('--read_topic', type=str, default=os.getenv("KAFKA_TOPIC", "input"),
                            help='Kafka topic name to read messages from')
    argparser.add_argument("--master", type=str,
                            default=os.getenv("SPARK_MASTER", "spark://spark-master-server:7077"),
                            help="Spark master URL")
    argparser.add_argument("--app_name", type=str, default="Kafka-Spark-Cassandra", 
                            help="Name of the Spark application")
    argparser.add_argument("--log_level", type=str, choices=["WARN", "INFO", "DEBUG"],
                            help="Log level for the Spark context", default="WARN")
    argparser.add_argument("--cassandra_host", type=str, 
                            default=os.getenv("CASSANDRA_HOST", "cassandra"),
                            help="Cassandra host")
    argparser.add_argument("--cassandra_port", type=str, default=os.getenv("CASSANDRA_PORT", "9042"),
                            help="Cassandra port")
    argparser.add_argument("--keyspace", type=str, default=os.getenv("CASSANDRA_KEYSPACE", "wiki"),
                           help="Cassandra keyspace")
    args = argparser.parse_args()
    main(args)
