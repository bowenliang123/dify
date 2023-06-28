PROJECT_PATH=$(cd `dirname $0`/..; pwd)

cd $PROJECT_PATH/docker

docker compose -f docker-compose.middleware.yaml up -d
