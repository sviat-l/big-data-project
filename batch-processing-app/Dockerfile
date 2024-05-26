FROM python:3.10-slim

WORKDIR /app

COPY batch-processing-app /app
COPY rest-app /app/db
COPY rest-app/cassandra_client.py /app/db/cassandra-client.py
COPY rest-app/cassandra_processing.py /app/db/cassandra_processing.py
COPY rest-app/mongo_processing.py /app/db/mongo_processing.py

RUN pip install --no-cache-dir -r requirements.txt

ENV CASSANDRA_HOST cassandra
ENV CASSANDRA_PORT 9042
ENV CASSANDRA_KEYSPACE wiki

ENV PYTHONPATH .:db

CMD ["python", "batch_processing.py"]
