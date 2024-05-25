FROM python:3.10-slim

WORKDIR /app

COPY . /app
COPY ../rest-app /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CASSANDRA_HOST cassandra
ENV CASSANDRA_PORT 9042
ENV CASSANDRA_KEYSPACE wiki

CMD ["python", "batch_processing.py"]
