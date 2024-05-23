#!/bin/bash

topic=input
if [ $# -eq 1 ]; then
    topic=$1
fi

# run console consumer
docker exec -it kafka-server kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic $topic \
