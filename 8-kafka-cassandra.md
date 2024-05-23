
# Homework 8: 🤖 Kafka Cassandra Rest

Author: **Sviatoslav Lushnei**

## 📝 Description

Creating a REST API that provides the data from the Cassandra database, that is populated from the Kafka topic with the data from the file.

## Structure:

### 1. Folders:
- [`./kafka-producer`](./kafka-producer) - folder with the Kafka producer app program with the Dockerfile, reads the data from the file and sends it to the Kafka topic
- [`./kafka-cassandra`](./kafka-cassandra) - folder with the Kafka-Cassandra app, reads the data from the Kafka topic and writes it to the Cassandra DB
- [`./rest-app`](./rest-app) - folder with the REST API app, reads the data from the Cassandra DB and provides the REST API for the user to get the data
- [`./scripts`](./scripts) - folder with all bash scripts for running the cluster, building the images, running all apps, and stopping the cluster
- [`./results`](./results) - folder with the results of the testing with images and probably some other files

--- 

### 2. Scripts (yes there are a lot of them)


There are general scripts that can take arguments and run the necessary commands, and also there are specified scripts for running concrete apps.

#### Clusters and cassandra scripts:

- [`./scripts/run-kafka-cluster.sh`](./scripts/run-kafka-cluster.sh), [`.scripts/run-cassandra.sh`](./scripts/run-cassandra.sh) - scripts for running the Kafka cluster and Cassandra (it uses the `docker-compose.yaml` file).
- -  After init the topic `transactions` will be created in the Kafka cluster and the same in the Cassandra DB (the keyspace `transactions`)
- - With the tables: `transactions.client_transactions`, `transactions.transactions_by_date`, with the DDL from the `./scripts/ddl.cql` file
- [`./scripts/shutdown-cluster.sh`](./scripts/shutdown-cluster.sh) and [`./scripts/shutdown-cassandra.sh`](./scripts/shutdown-cassandra.sh) - scripts for stopping the Kafka cluster and Cassandra

- - -

#### Apps build scripts:
- [`./scripts/build-producer-app-image.sh`](./scripts/build-producer-app-image.sh), [`./scripts/build-kafka-cassandra-app-image.sh`](./scripts/build-kafka-cassandra-app-image.sh), [`./scripts/build-rest-app-image.sh`](./scripts/build-rest-app-image.sh) - scripts for building the images for the producer app, Kafka-Cassandra app, and the REST API

- [`./scripts/build-app-image.sh`](./scripts/build-app-image.sh) - script for building the image for the app (it has one argument app_name to build the specified app image)
Possible app names: `kafka-producer`, `kafka-cassandra`, `rest`
Usage example:
```bash
sh scripts/build-app-image.sh kafka-producer
```

Note that the images will be built with the tag `latest` and the name `kafka-producer-app`, `kafka-cassandra-app`, `rest-app` respectively, and the previous images with be deleted.

- [`./scripts/shutdown-app-container.sh`](./scripts/shutdown-app-container.sh) - script for stopping the app (it has one argument app_name to stop the specified app)
Possible app names: `kafka-producer`, `kafka-cassandra`, `rest`
Usage example:
```bash
sh scripts/shutdown-app-container.sh kafka-cassandra
```
- - -

#### Run app container scripts:

- [`./scripts/run-kafka-producer-app.sh`](./scripts/run-kafka-producer-app.sh), [`./scripts/run-kafka-cassandra-app.sh`](./scripts/run-kafka-cassandra-app.sh), [`./scripts/run-rest-app.sh`](./scripts/run-rest-app.sh) - scripts for running the producer app, Kafka-Cassandra app, and the REST API. The container will be automatically removed after stopping the app. They have an optional argument command to run in the console:

```bash
sh scripts/run-{app-name}.sh <command>
# <command> may be empty or contain the command to run in the console 
# (if it is empty it will run the default app command)
# Note: the command should be in quotes if it contains spaces
```

Here are some examples:
```bash
sh scripts/run-kafka-producer-app.sh bash
sh scripts/run-kafka-cassandra-app.sh "python main.py --help"
sh scripts/run-rest-app.sh
```
- - - 

### 3. Kafka-Producer app

- [`./kafka-producer-app`](./kafka-producer-app) - folder with the kafka-producer app program with the Dockerfile

- [`Dockerfile`](./kafka-producer-app/Dockerfile) and [`requirements.txt`](./kafka-producer-app/requirements.txt) - files with the Dockerfile for the producer app and the reqirements installation

- [`./producer-app/data`](./kafka-producer-app/data) - folder with the data for the producer app, it contains `transactions.csv` files with the data for the producer app, 75000 rows enough to run the producer app for 50 minutes with the default latency of 0.04s (25 messages per second)

- - - 
- [`./producer-app/main.py`](./kafka-producer-app/main.py) - file with the producer app program (you can run it with `python main.py`, to get the possible arguments run `python main.py --help`).
- - You can run the producer app in the container using the script `run-kafka-producer-app.sh` with the commands.

- - - 

### 4. Kafka-Cassandra app

- [`./kafka-cassandra-app`](./kafka-cassandra-app) - folder with the app program for kafka-cassandra communication (read from Kafka and write to Cassandra)

- [`Dockerfile`](./kafka-cassandra-app/Dockerfile) and [`requirements.txt`](./kafka-cassandra-app/requirements.txt) - files with the Dockerfile for the consumer app and the reqirements installation

- [`abstract_cassandra_db.py`](./kafka-cassandra-app/abstract_cassandra_db.py) - file with the abstract class for the Cassandra DB, that has the methods for the connection, and operations with the DB

- [`cassandra_models.py`](./kafka-cassandra-app/cassandra_models.py) - file with the models schemas for the Cassandra DB, that has the classes for the tables: `ClientTransactions`, `TransactionsByDate`, and `BaseModel` as the base class (abstract) for the other models.

- [`./kafka-cassandra-app/main.py`](./kafka-cassandra-app/main.py) - file with the consumer app program you can run it with shell in its container, to get the possible arguments run `python main.py --help`

- - -

### 5. REST app

- [`./rest-app`](./rest-app) - folder with the REST API app program with the Dockerfile

- [`Dockerfile`](./rest-app/Dockerfile) and [`requirements.txt`](./rest-app/requirements.txt) - files with the Dockerfile for the REST API app and the reqirements installation

- [`rest_models.py`](./rest-app/rest_models.py) - file with the rest models (table schemas) that defines the structure of output data, that will be returned by the API.(what will be seen on the API)

- [`cassandra_processing.py`](./rest-app/cassandra_processing.py) - file with the main logic of the getting results from the cassandra database and their processing. As a transport layer between the cassandra database and the rest application. (what to get from the database and how to process it)

- [`cassandra_client.py`](./rest-app/cassandra_client.py) - file with the cassandra client that connects to the cassandra database and executes the queries for the specified purposes.(how to execute the queries to the database)

- [`rest_application.py`](./rest-app/rest_application.py) - source file with the rest application, here the main logic of the application is implemented, with endpoints and the logic of the endpoints. Stand for the provided API.

### 6. Other important files:
- [`./docker-compose.yaml`](./docker-compose.yaml) - file with the configuration for the Kafka cluster and Cassandra, it has 3 services: `kafka`, `cassandra`, `zookeeper`. So you can run the as in the example below:
```bash
docker compose up -d --wait kafka zookeeper
```
```bash
docker compose down cassandra
```
Also you can run both cassandra and kafka with just the `docker compose up -d --wait` command and stop them with `docker compose down`

- [`start-all.sh`](./start-all.sh) - script for running all the apps and the cluster, and cassandra (it uses the `docker-compose.yaml` file)
- [`delete-all.sh`](./delete-all.sh) - script for stopping and removing all the containers and images
- [`build-all.sh`](./build-all.sh) - script for building all the images for the apps (delete the previous images and build the new ones), it uses the `build-app-image.sh` script with the app names as arguments (kafka-producer, kafka-cassandra, rest)

- [`ddl.cql`](/ddl.cql) - file with the DDL for the Cassandra DB, that creates the keyspace `transactions` and the tables: `transactions.client_transactions`, `transactions.transactions_by_date`


## 📚 Tables design

### 0. Some notes about the data, and decisions made
- There are no unique identifiers for the transactions, so I decided to use the `transaction_id` as the unique identifier for the transactions with `UUID` type.
- Tables are designed to answer the questions **without** using the `ALLOW FILTERING` in the queries.
- The data is about the transactions, so the tables are designed to specifically answer the questions. Selected columns that are needed for the questions. (so as there were no specific requirements about the data, I decided to use the only a few columns, definitely they can be extended or changed if needed)


### 1. **Client transactions** - table with the transactions data from the clients
```sql
CREATE TABLE IF NOT EXISTS transactions.client_transactions (
    transaction_id UUID,
    type TEXT,
    amount DECIMAL,
    name_orig TEXT,
    oldbalance_orig TEXT,
    newbalance_orig TEXT,
    name_dest TEXT,
    is_fraud BOOLEAN,
    transaction_date TEXT,
    PRIMARY KEY ((name_orig, is_fraud), amount, transaction_id)
) WITH CLUSTERING ORDER BY (amount DESC);
```
With the key `name_orig`, `is_fraud`, and ordered by `amount`. the table is designed to answer for questions:
- get transactions for the specified client that are fraud
- get 3 most expensive transactions for the specified client

To get those results there are used queries with the specified `name_orig`, `is_fraud`, with `LIMIT N` if needed, and the processing stage that selects the needed data from the results.

Columns here corresponds to both transaction endes, amount and user balance change with some transactions info such as (type, date, fraud status). So it contains almost all the data about the transaction.

### 2. **Transactions by date** - table with the transactions data from the clients by date
```sql
CREATE TABLE IF NOT EXISTS transactions.transactions_by_date(
    transaction_date TEXT,
    transaction_id UUID,
    name_dest TEXT,
    name_orig TEXT,
    amount DECIMAL,
    type TEXT,
    is_fraud BOOLEAN,
    PRIMARY KEY ((transaction_date, name_dest), transaction_id)
);
```
With the key `transaction_date`, `name_dest`, and `transaction_id` to make full primary key. That 'trick' with setting date as part of partitioning key enables using queries **without** `ALLOW FILTERING`.


The table is designed to answer for question:
- get total amount of inflow transactions for the specified client for the specified date range

It is done by iterating over each date from the specified date range, and for each date, getting the transactions for the specified client, and summing the amount of the transactions.

- As here we need to get the total amount from the transactions to the specified client, the table contains the columns that are needed for the calculation of the total amount of the transactions, and some other collumn that may be used for futher analysis. 
- For example to find distribution of the transactions by the type, is fraud analyzis. 
- The minimal sufficient data to answer the question may contain only the `[transaction_date, name_dest, amount, transaction_id]` columns.


## ALL API's

### 0. Run container api review
The container will be automatically removed after stopping the app. They have an optional argument command to run in the console:
App names: `kafka-producer`, `kafka-cassandra`, `rest`

```bash
sh scripts/run-{app-name}.sh <command>
# <command> may be empty or contain the command to run in the console 
# (if it is empty it will run the default app command)
# Note: the command should be in quotes if it contains spaces
```

Here are some examples:
- you can get into the container with the bash console with the following command:
```bash
sh scripts/run-kafka-producer-app.sh bash
```
- or run directly the command in the container:
```bash
sh scripts/run-kafka-cassandra-app.sh "python main.py --help"
```
- or use default command, that will do all the work:
```bash
sh scripts/run-rest-app.sh
```

### 1. Kafka-Producer app API
You can run the producer app in the container using the script `run-kafka-producer-app.sh` with the commands.

```bash
sviat@sviat-Swift-SF314-42:~/code/bdata/8_Kafka-Cassandra-REST$ sh scripts/run-kafka-producer-app.sh "python main.py --help"
Command to run: python main.py --help
usage: main.py [-h] [--file_path FILE_PATH] [--bootstrap_servers BOOTSTRAP_SERVERS] [--topic TOPIC] [--log_every LOG_EVERY] [-n LIMIT] [--latency LATENCY]

options:
  -h, --help            show this help message and exit
  --file_path FILE_PATH
                        Path to the file containing data
  --bootstrap_servers BOOTSTRAP_SERVERS
                        Kafka server address
  --topic TOPIC         Kafka topic name to write to
  --log_every LOG_EVERY
                        Log every n messages, (-1 or 0 to disable)
  -n LIMIT, --limit LIMIT
                        Limit the number of messages to post (-1 to post all)
  --latency LATENCY     Latency between messages in s
kafka-producer-app-server container exited
```

So you can run the producer app in container with the following command (it is run by the default command):
```bash
sh scripts/run-kafka-producer-app.sh "python main.py --file_path data/transactions_75k.csv --log_every 5000 --latency 0.04 --topic transactions --bootstrap_servers kafka-server:9092 --limit -1"
```
Here is another example with the bash console:
``` bash
sh scripts/run-kafka-producer-app.sh "python main.py --log_every 1000 --limit 10000"
```

### 2. Kafka-Cassandra app API

You can run the consumer app in the container using the script `run-kafka-cassandra-app.sh` with the commands, if empty it will run the default command.
```bash
sh scripts/run-kafka-cassandra-app.sh <command>
# <command> may be empty or contain the command to run in the console
```

```bash
sviat@sviat-Swift-SF314-42:~/code/bdata/8_Kafka-Cassandra-REST$ sh scripts/run-kafka-cassandra-app.sh "python main.py --help"
Command to run: python main.py --help
usage: main.py [-h] [--bootstrap-servers BOOTSTRAP_SERVERS] [--topic TOPIC] [--host HOST] [--port PORT] [--keyspace KEYSPACE] [--log_every LOG_EVERY] [--limit LIMIT]

Read messages from Kafka topic and write to Cassandra DB.

options:
  -h, --help            show this help message and exit
  --bootstrap-servers BOOTSTRAP_SERVERS
                        Kafka bootstrap servers
  --topic TOPIC         Kafka topic name to read messages from
  --host HOST           Cassandra host
  --port PORT           Cassandra port
  --keyspace KEYSPACE   Cassandra keyspace
  --log_every LOG_EVERY
                        Log every n messages processed
  --limit LIMIT         Limit the number of messages to process
kafka-cassandra-app-server container exited
```

So you can run the consumer app in container with the following command (it is run by the default command):
```bash
sh scripts/run-kafka-cassandra-app.sh "python main.py --bootstrap-servers kafka-server:9092 --topic transactions --host cassandra --port 9042 --keyspace transactions --log_every 5000 --limit -1"
```
More clean usage example:
```bash
sh scripts/run-kafka-cassandra-app.sh "python main.py --log_every 10000"
```
### 3. REST API app

#### Running the REST API app
To run the REST API app in the container you can use the script `run-rest-app.sh`
```bash
sh scripts/run-rest-app.sh
# by default it will run the app with the command
# uvicorn rest_application:app --host 0.0.0.0 --port 8080
```
It is the same as running the following command:

The app will be available on the `http://0.0.0.0:8080`.

### 📦 Available endpoints
0. ``http://0.0.0.0:8080/docs`` - the docs for the API, with the available endpoints, and the parameters for the endpoints.

1. `/users/{user_id}/transactions/?is_fraud=True` - get transactions for the user with the specified `user_id` that are marked as fraud

Example: `http://0.0.0.0:8080/users/C2026325575/transactions?is_fraud=True`

2. `/users/{user_id}/transactions/?limit=3` - get 3 most expensive transactions for the user with the specified `user_id`

Example: `http://0.0.0.0:8080/users/C1508750581/transactions?limit=3`
Return format for first two endpoints:

```json
[
  {
    "transaction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "transaction_date": "2024-04-25",
    "name_orig": "string",
    "name_dest": "string",
    "amount": 100.00,
    "is_fraud": true
  }
]
```

3. `/users/{user_id}/total-inflow/?start_date={FROM}&end_date={TO}` - get total amount of inflow transactions for the user with the specified `user_id` for the specified date range

Example: `http://0.0.0.0:8080/users/C985934102/total-inflow/?start_date=2024-03-04&end_date=2024-05-05`


Return format:
```json
[
  {
    "user_id": "string",
    "total_inflows": "string",
    "start_date": "2024-04-05",
    "end_date": "2024-04-25",
    "num_transactions": 0
  }
]
```


Also there is error handling for the endpoints, as (wrong date format, wrong date range, limit is not in the range, etc.)
, and the error messages are returned in the format:
```json
{
  "detail": "Error Message"
}
```

And the validation error in the format:
```json
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

**Notes** 
- if you try to get the data for the date range that is not present in the database, you will get the empty list, as there are no data for that date range or that parameters. 
- But if you try to get the data for the date range that is not in the correct format, you will get the error message, the same with the user id.

## 🖥 Usage Instructions

There are many scripts that can run the apps separately, build the images, run the containers, and stop them. (see the description above)

### 1. Kafka and Cassandra cluster
There is docker compose file that can run the whole application with the Kafka cluster and Cassandra. It contains the services: `kafka`, `zookeeper`, `cassandra`.

The easiest way to run the application is to run:
```bash
docker compose up -d --wait
```

Or you can run sepparately the kafka cluster and the cassandra with the following command:
1. Kafka and Zookeeper
```bash
docker compose up -d --wait kafka zookeeper # or sh scripts/run-kafka-cluster.sh
```
2. Cassandra
```bash
docker compose up -d --wait cassandra #or sh scripts/run-cassandra.sh
```

**Note** 
- It will create the topics in the Kafka cluster and the keyspace with the tables in the Cassandra DB, after initialization.
- Please wait until the containers are up and running healthy, before manually running the apps. It takes approximately 1 minute to start the Cassandra DB.

And the same for stopping the containers. but with the `down` command, or `shutdown-{server}.sh`.

### 2. Building the images
In the easiest way, you can build the images for the apps with the following command:

```bash
sh build-all.sh
```

To build the images separately you can use the following commands and the app names as arguments for the `build-app-image.sh` script:
```bash
sh scripts/build-app-image.sh kafka-producer
sh scripts/build-app-image.sh kafka-cassandra
sh scripts/build-app-image.sh rest
```

Or using separete scripts:
```bash
sh scripts/build-producer-app-image.sh
sh scripts/build-kafka-cassandra-app-image.sh
sh scripts/build-rest-app-image.sh
```

### 3. Running the apps
To run the apps you can use the scripts that are described above, by default they will run the apps with the default commands, but you can specify the command to run in the container (the API is described above)

- Kafka producer app
```bash
sh scripts/run-kafka-producer-app.sh
# it is the same as running
# sh scripts/run-kafka-producer-app.sh "python main.py"
```

- Kafka-Cassandra app
```bash
sh scripts/run-kafka-cassandra-app.sh
```

- REST API app
```bash
sh scripts/run-rest-app.sh
```


### 4. Stopping the apps
And to shutdown the apps you can use the following scripts:
```bash
sh scripts/shutdown-app-container.sh <app_name>
```

Where the app_name is one of the following: `kafka-producer`, `kafka-cassandra`, `rest`

```bash
sh scripts/shutdown-app-container.sh kafka-producer
sh scripts/shutdown-app-container.sh kafka-cassandra
sh scripts/shutdown-app-container.sh rest
```

### 5. Stopping the cluster
To stop the cluster you can use the following command:
```bash
docker compose down
```

Or you can use the following scripts:
```bash
sh scripts/shutdown-kafka-cluster.sh
sh scripts/shutdown-cassandra.sh
```

If you want to stop the cluster and remove the images you can use the following script:
```bash
sh delete-all.sh
```

## 📋 Fast start

1. Run the Kafka and Cassandra cluster
```bash
docker compose up -d --wait
```

2. Build the images for the apps
```bash
sh build-all.sh
```

Or use the following commands to start first two steps
```bash
sh start-all.sh
```
**Note** remember to wait until the containers are up and running healthy, before manually running the apps (the start script will wait for the containers to be healthy, but if you try to run manually, please wait until the containers are up and running)

3. Run the Kafka producer app
```bash
sh scripts/run-kafka-producer-app.sh
```

4. Run the Kafka-Cassandra app
```bash
sh scripts/run-kafka-cassandra-app.sh
```

5. Run the REST API app
```bash
sh scripts/run-rest-app.sh
```

6. Stop and remove the containers and images
```bash
sh delete-all.sh
```


## 📊 Results

1. All containers are up and running
- docker compose up
![Cluster](./results/img/1_composeUp.png)
- docker ps
![Cluster](./results/img/1_containers.png)

2. Topic and tables are created
- Kafka topic
![Topic](./results/img/2_topic.png)
- Cassandra tables
![Tables](./results/img/2_tables.png)

3. Images are built
![Images](./results/img/3_images.png)

4. Kafka producer app results
- The producer app is running and sending the messages to the Kafka topic
![Producer](./results/img/4_producer.png)
- We can see the messages in the Kafka topic with client CLI
![Kafka](./results/img/4_kafka_messages.png)

5. Kafka-Cassandra app results
- The Kafka-Cassandra app is running and reading the messages from the Kafka topic and writing them to the Cassandra DB
![Kafka-Cassandra](./results/img/5_kafka-cassandra.png)

- inserted records in the Cassandra DB
![Cassandra](./results/img/5_cassandra_records.png)

6. REST APP docs
![Docs](./results/img/6_rest_docs.png)

7. REST API results

### Basic Queries

- get transactions for the user with the specified `user_id` that are marked as fraud

`http://0.0.0.0:8080/users/C858959216/transactions?is_fraud=True`

![Fraud](./results/img/7_fraud.png)

- get 3 most expensive transactions for the user with the specified `user_id`

`http://0.0.0.0:8080/users/C2047521920/transactions?limit=3`

![Expensive](./results/img/7_expensive.png)

### Inflow Transactions
- get total amount of inflow transactions for the user with the specified `user_id` for the specified date range

`http://0.0.0.0:8080/users/C248609774/total-inflow/?start_date=2024-04-20&end_date=2024-04-24`

![Inflow1](./results/img/7_inflow-narrow.png)

`http://0.0.0.0:8080/users/C248609774/total-inflow/?start_date=2024-04-01&end_date=2024-04-24`

![Inflow2](./results/img/7_inflow-wide.png)

### Error handling and Edge cases

- Wrong path uid `http://0.0.0.0:8080/users/1/transactions`

![Wrong](./results/img/7_wrong_path.png)

- Wrong query params `http://0.0.0.0:8080/users/C248609774/total-inflow/?start_date=2024-04-31&end_date=2024-04-24`
![Error](./results/img/7_wrong_params.png)

- Empty results `http://0.0.0.0:8080/users/C248609774/total-inflow/?start_date=2024-04-24&end_date=2024-04-24`
![Empty](./results/img/7_empty.png)

- Validation error `http://0.0.0.0:8080/users/C248609774/total-inflow/?start_date=2024-04-30`
![Empty](./results/img/7_validation_error.png)

8. Stopping the cluster
- docker compose down with delete all
![Down](./results/img/8_shutdown-all.png)


9. Showing the kafka-cassandra-app with few records

- before running the app
![Kafka-Cassandra](./results/img/9_rest-app-0.png)

- The app is running and processing the messages from the Kafka topic
![Kafka-Cassandra](./results/img/9_kafka-insert.png)

- The records are inserted in the Cassandra DB
![Cassandra1](./results/img/9_cassandra-insert.png)
![Cassandra2](./results/img/9_cassandra-select.png)

- Results from the REST API
![REST1](./results/img/9_rest-app-1.png)
![REST2](./results/img/9_rest-app-2.png)
![REST3](./results/img/9_rest-app-3.png)


**Note**
The results may differ from the screenshots, as the data is generated smoothly.

## 📌 Notes
- _All the results of the test are located in the [`results`](./results) folder with the screenshots of the console output._

- _the tables are designed to answer the questions without using the `ALLOW FILTERING` in the queries._

- _As there are a lot of text in the README file, there may be some mistakes(_


