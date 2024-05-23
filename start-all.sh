#!/bin/bash

docker compose up --wait

sh scripts/build-app-image.sh
sh scripts/run-endpoint-app.sh &
sh scripts/spark-kafka-run.sh &
sh scripts/spark-cassandra-run.sh &

wait
