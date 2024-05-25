#!/bin/bash

command=$1
if [ -z "$command" ]; then
    command="
    spark-submit --deploy-mode client\
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0\
    /app/kafka-cassandra.py
    "
fi

container_name="app-spark-cassandra-server"

docker rm -f $container_name >/dev/null 2>&1 || true

docker run --rm \
        --network wiki-streaming-network \
        --name $container_name \
        -v $(pwd)/cassandra-populating-app:/app \
        -it bitnami/spark:3 \
        $command

echo "$app_name container exited"
