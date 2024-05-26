## Intro

Project name, link to the repository, and a brief description of the project.
## How to run
```bash
docker compose up -d
```
open `http://localhost:4200/docs` in your browser

to stop the project
```bash
docker compose down
```

## Diagram

A diagram of the project's architecture. DataFlow
4.5 steps:
read, preprocess, store, precalulate, serve

### Services Description/Motivation
- main db choosed
- additional db choosed
- kafka/spark
- **Endpoint-reader**: 
- **cassandra-populating**:
- **batch-processing**
- rest app

## Data Models
### Cassandra tables

- table1, ddl, motimation, for what is used
- table2, ddl, motimation, for what is used
- table3, ddl, motimation, for what is used
- table4, ddl, motimation, for what is used
- table5, ddl, motimation, for what is used


### MongoDB
-document 1
-document 2
-document 3

## Endpoints

### Ah-hoc
1. `GET /domains/all` - returning information about all domains with created pages
- endpoint `GET /domains/all` + description or fastapi docs screenshot
- return schema, description or fastapi docs screenshot
2. ...

### Pre-calculated
...

## Results
### Ad-hoc
1, 2, 3, 4, 5
### Pre-calculated
1, 2, 3


## Add-on:
- repository structure
