#!/bin/bash

app_name=$1
if [ -z "$app_name" ]; then
    app_name=endpoint-reader-app
fi
app_dir=./$app_name

docker rmi $app_name --force
docker build -t $app_name $app_dir
