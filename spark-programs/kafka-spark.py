import argparse
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.streaming import StreamingQuery
import pyspark.sql.functions as F

def create_spark_session(app_name: str, master: str, log_level: str, cores_max:int=1, executor_mem:str='1g') -> SparkSession:
    """Creating the Spark session with the given configurations."""
    spark_session = SparkSession \
            .builder \
            .appName(app_name) \
            .config("spark.streaming.stopGracefullyOnShutdown", True) \
            .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0') \
            .config("spark.sql.shuffle.partitions", 4) \
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

def write_kafka_stream(df: DataFrame, bootstrap_servers: str, topic: str) -> StreamingQuery:
    """Write messages to Kafka topic as a stream."""
    return df.writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_servers) \
            .option("topic", topic) \
            .option("checkpointLocation", "/tmp/checkpoint") \
            .start()
            
def streaming_console_output(df: DataFrame) -> StreamingQuery:
    """Output the DataFrame to the console."""
    return df.writeStream \
            .format("console") \
            .outputMode("append") \
            .start()

def process_data(input_df: DataFrame) -> DataFrame:
    """Process the input data and return the filtered data."""
    # Selecting the data from the input stream message
    data_df = input_df\
            .selectExpr("CAST(value AS STRING)")\
            .filter(F.expr("value LIKE 'data: %'"))\
            .select(F.expr("substring(value, 7) AS data"))
    # Parsing the JSON data BASED on the schema     
    parsed_df = data_df\
            .selectExpr("from_json(data, 'struct<"+
                "meta:struct<domain:string, request_id:string>, "+
                "performer:struct<user_is_bot:boolean, user_id:integer>, "+
                "dt:string, "+
                "page_title:string>') AS data")\
            .select("data.*")
    # Filtering the data based on the conditions
    filtered_df = parsed_df.filter(
        F.expr("meta.domain IN ('en.wikipedia.org', 'www.wikidata.org', 'commons.wikimedia.org')") &
        (~F.expr("performer.user_is_bot"))
    )
    # Selecting the required columns, with naming convention
    selected_df = filtered_df.select(
            F.col("meta.domain").alias("domain"),
            F.col("meta.request_id").alias("request_id"),
            F.col("performer.user_id").alias("user_id"),
            F.col("dt").alias("created_at"),
            F.col("page_title"))
    print("Schema of the selected data:")
    selected_df.printSchema()
    # Formatting the output string to be written to Kafka
    formatted_df = selected_df \
            .withColumn("value", F.to_json(
                F.struct("domain", "request_id", "user_id", "created_at", "page_title"))
                        )\
            .selectExpr("CAST(value AS STRING)")
    return formatted_df


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
    """
    spark_session = create_spark_session(args.app_name, args.master, args.log_level, 
                                         args.cores_max, args.executor_mem)
    print("Reading from Kafka topic: ", args.read_topic)
    input_df = read_kafka_stream(spark_session, args.bootstrap_servers, args.read_topic)
    output_df = process_data(input_df)
    print("Writing to Kafka topic: ", args.write_topic)
    write_querry = write_kafka_stream(output_df, args.bootstrap_servers, args.write_topic)
    write_querry.awaitTermination()
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Read messages from Kafka topic, filter them, and write to another Kafka topic.')
    argparser.add_argument('--bootstrap-servers', type=str,
                        default="kafka:9092", help='Kafka bootstrap servers')
    argparser.add_argument('--read_topic', type=str, default="input",
                        help='Kafka topic name to read messages from')
    argparser.add_argument('--write_topic', type=str, default="processed",
                        help='Kafka topic name to write filtered messages to')
    argparser.add_argument("--master", type=str,
                           default="spark://spark-master-server:7077", help="Spark master URL")
    argparser.add_argument("--app_name", type=str,
                            default="Kafka-Spark-Kafka", help="Name of the Spark application")
    argparser.add_argument("--log_level", type=str, default="WARN", choices=["WARN", "INFO", "DEBUG"],
                           help="Log level for the Spark context")
    argparser.add_argument("--cores_max", type=int, default=1, help="Maximum number of cores to use")
    argparser.add_argument("--executor_mem", type=str, default="1g", help="Memory allocated to each executor")
    args = argparser.parse_args()
    main(args)
