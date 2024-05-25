FROM bitnami/spark:3

WORKDIR /app
COPY . /app

ENV CASSANDRA_HOST cassandra
ENV CASSANDRA_PORT 9042
ENV CASSANDRA_KEYSPACE wiki
ENV KAFKA_BOOTSTRAP_SERVERS kafka:9092
ENV KAFKA_TOPIC input
ENV SPARK_MASTER spark://spark-master-server:7077

CMD ["spark-submit", "--deploy-mode=client", "--packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0", "/app/kafka-cassandra.py"]
CMD ["bash"]