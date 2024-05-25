FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CASSANDRA_HOST cassandra
ENV CASSANDRA_PORT 9042
ENV CASSANDRA_KEYSPACE wiki

ENV APP_HOST 0.0.0.0
ENV APP_PORT 4200

CMD ["sh", "-c", "uvicorn rest_application:app --host $APP_HOST --port $APP_PORT --reload"]
