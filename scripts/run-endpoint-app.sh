
command=$1

app_name=endpoint-reader-app
app_dir=./$app_name
app_container=$app_name-server
network=wiki-streaming-network

docker rm -f $app_container >/dev/null 2>&1 || true

docker run --rm \
        --network $network \
        --name $app_container \
        --volume $(pwd)/$app_dir:/app \
        -it $app_name \
        $command
    
echo "Producer app container exited"
