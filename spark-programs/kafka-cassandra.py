import argparse
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.streaming import StreamingQuery

def create_spark_session(app_name: str, master: str, log_level: str, 
                         cassandra_host: str="cassandra", cassandra_port: str="9042",
                         cores_max:int=1, executor_mem:str='1g') -> SparkSession:
    """Creating the Spark session with the given configurations."""
    spark_session = SparkSession \
            .builder \
            .appName(app_name) \
            .config("spark.streaming.stopGracefullyOnShutdown", True) \
            .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0'+
                                           ',com.datastax.spark:spark-cassandra-connector_2.12:3.1.0') \
            .config("spark.sql.shuffle.partitions", 4) \
            .config("spark.cassandra.connection.host", cassandra_host) \
            .config("spark.cassandra.connection.port", cassandra_port) \
            .config("spark.executor.memory", executor_mem) \
            .config("spark.cores.max", cores_max) \
            .master(master) \
            .getOrCreate()
    spark_session.sparkContext.setLogLevel(log_level)
    return spark_session

def read_kafka_stream(spark: SparkSession, bootstrap_servers: str, topic: str) -> DataFrame:
    """Read messages from Kafka topic as a stream."""
    return spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_servers) \
            .option("subscribe", topic) \
            .load()
            
def streaming_console_output(df: DataFrame) -> StreamingQuery:
    """Output the DataFrame to the console."""
    return df.writeStream \
            .outputMode("append") \
            .format("console") \
            .start()

def write_to_cassandra(df: DataFrame, keyspace: str, table: str) -> StreamingQuery:
    """Write messages to Cassandra table as a stream."""
    df = df.selectExpr("request_id", "user_id", "domain", "user_text", "created_at", "page_title")
    return df.writeStream \
            .foreachBatch(lambda batch_df, batch_id: 
                batch_df.write \
                    .format("org.apache.spark.sql.cassandra") \
                    .options(table=table,keyspace=keyspace
                    ).mode("append").save()
            ).start()
            
def save_to_cassandra_table(df: DataFrame, keyspace: str, table: str):
    """ Write data to a Cassandra table."""
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(table=table,keyspace=keyspace
        ).mode("append").save()
            
def write_all_to_cassandra(df: DataFrame, keyspace: str):
    """ Write data to all tables in the keyspace."""
    domain_articles_df = df.select("domain", "page_id")
    save_to_cassandra_table(domain_articles_df, keyspace, "domain_articles")
    user_pages_df = df.select("user_id", "page_id", "page_title")
    save_to_cassandra_table(user_pages_df, keyspace, "user_pages")
    pages_df = df.select("page_id", "page_title", "domain")
    save_to_cassandra_table(pages_df, keyspace, "pages")
    pages_by_date_df = df.select("created_at", "page_id", "page_title", "user_id", "user_text", "domain")
    save_to_cassandra_table(pages_by_date_df, keyspace, "pages_by_date")
    domain_stats_df = df.select("domain", "page_id", "created_at", "user_is_bot")
    save_to_cassandra_table(domain_stats_df, keyspace, "domain_stats")
    
def start_cassandra_write(df: DataFrame, keyspace: str, table: str) -> StreamingQuery:
    return df.writeStream \
        .foreachBatch(write_all_to_cassandra) \
        .start()

def process_data(input_df: DataFrame) -> DataFrame:
    """Process the input data and return in the format to write to Cassandra."""
    data_df = input_df.selectExpr("CAST(value AS STRING)")
    parsed_df = data_df\
            .selectExpr("from_json(value, 'struct<"+
                "domain:string, "+ 
                "request_id:string, "+
                "user_id:integer, "+
                "user_text:string, "+
                "user_is_bot:boolean, "+
                "created_at:string, "+
                "page_id:integer,"
                "page_title:string>') AS data")\
            .select("data.*")
    return parsed_df


def main(args: argparse.Namespace):
    """ Read messages from Kafka topic, filter them, and write to another Kafka topic.
    Args:
    args.boostrap_servers: Kafka bootstrap servers
    args.read_topic: Kafka topic name to read messages from
    args.write_topic: Kafka topic name to write filtered messages to
    args.master: Spark master URL
    args.app_name: Name of the Spark application
    args.log_level: Log level for the Spark context
    args.cores_max: Maximum number of cores to use
    args.executor_mem: Memory allocated to each executor
    args.cassandra_host: Cassandra host
    args.cassandra_port: Cassandra port
    args.keyspace: Cassandra keyspace write to
    args.table: Cassandra table name
    """
    spark_session = create_spark_session(args.app_name, args.master, args.log_level, 
                    args.cassandra_host, args.cassandra_port,args.cores_max, args.executor_mem)
    print("Reading from Kafka topic: ", args.read_topic)
    input_df = read_kafka_stream(spark_session, args.bootstrap_servers, args.read_topic)
    processed_df = process_data(input_df)
    print("Writing to Cassandra table:", f"{args.keyspace}.{args.table}")
    print("Output Schema:")
    processed_df.printSchema()
    write_query = write_to_cassandra(processed_df, args.keyspace, args.table)
    # write_query = write_all_to_cassandra(processed_df, args.keyspace)
    write_query.awaitTermination()
    
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Read messages from Kafka topic and write to Cassandra.')
    argparser.add_argument('--bootstrap-servers', type=str,
                        default="kafka:9092", help='Kafka bootstrap servers')
    argparser.add_argument('--read_topic', type=str, default="processed",
                        help='Kafka topic name to read messages from')
    argparser.add_argument("--master", type=str,
                           default="spark://spark-master-server:7077", help="Spark master URL")
    argparser.add_argument("--app_name", type=str,
                            default="Kafka-Spark-Cassandra", help="Name of the Spark application")
    argparser.add_argument("--log_level", type=str, default="WARN", choices=["WARN", "INFO", "DEBUG"],
                           help="Log level for the Spark context")
    argparser.add_argument("--cores_max", type=int, default=1, help="Maximum number of cores to use")
    argparser.add_argument("--executor_mem", type=str, default="1g", help="Memory allocated to each executor")
    argparser.add_argument("--cassandra_host", type=str, default="cassandra", help="Cassandra host")
    argparser.add_argument("--cassandra_port", type=str, default="9042", help="Cassandra port")
    argparser.add_argument("--keyspace", type=str, default="wiki", help="Cassandra keyspace")
    argparser.add_argument("--table", type=str, default="created_pages", help="Cassandra table")
    args = argparser.parse_args()
    main(args)
