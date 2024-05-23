#!/bin/bash

command=$1
if [ -z "$command" ]; then
    command="
    spark-submit --deploy-mode client\
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0\
    /opt/app/kafka-cassandra.py
    "
fi

container_name="app-spark-cassandra-server"

docker rm -f $container_name >/dev/null 2>&1 || true

docker run --rm \
        --network wiki-streaming-network \
        --name $container_name \
        -v $(pwd)/spark-programs:/opt/app \
        -it bitnami/spark:3 \
        $command

echo "Spark app container exited"
