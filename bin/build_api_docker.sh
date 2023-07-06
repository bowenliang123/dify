PROJECT_PATH=$(cd `dirname $0`/..; pwd)

echo ${PROJECT_PATH}
cd $PROJECT_PATH/api

docker build . -t dockertest.gf.com.cn/dataportal/dify-api

docker push dockertest.gf.com.cn/dataportal/dify-api
