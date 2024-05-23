#!/bin/bash

# Zookeeper and Kafka
docker stop zookeeper && docker rm zookeeper
docker stop kafka-server && docker rm kafka-server

# Spark master and worker
docker stop spark-master-server && docker rm spark-master-server
docker stop spark-worker-server && docker rm spark-worker-server

# Cassandra
docker stop cassandra-server && docker rm cassandra-server

# Endpoint app
docker stop producer-app-server && docker rm producer-app-server

# Kafka - Spark - Kafka
docker stop app-spark-kafka-server && docker rm app-spark-kafka-server

# Kafka - Spark - Cassandra App
docker stop app-spark-cassandra-server && docker rm app-spark-cassandra-server

# Network
docker network rm wiki-streaming-network
