
app_name=producer-app
app_dir=./$app_name

docker rmi $app_name --force

docker build -t $app_name $app_dir
