from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.streaming import StreamingQuery

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
            
def append_to_cassandra_table(df: DataFrame, keyspace: str, table: str):
    """ Write data to a Cassandra table."""
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(table=table,keyspace=keyspace
        ).mode("append").save()
