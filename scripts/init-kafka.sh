#!/bin/bash

kafka-topics.sh --create -if-not-exists --bootstrap-server kafka:9092 --replication-factor 1 --partitions 3 --topic input
kafka-topics.sh --create -if-not-exists --bootstrap-server kafka:9092 --replication-factor 1 --partitions 3 --topic processed
kafka-topics.sh --describe --bootstrap-server kafka:9092 --topic processed
