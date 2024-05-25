FROM python:3.10-slim

WORKDIR /app
COPY . /app

ENV KAFKA_TOPIC input
ENV KAFKA_BOOTSTRAP_SERVERS kafka:9092

RUN pip install -r requirements.txt
CMD ["python", "main.py"]
