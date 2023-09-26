PROJECT_PATH=$(cd `dirname $0`/..; pwd)

echo ${PROJECT_PATH}
cd $PROJECT_PATH/api

VERSION=0.3.6-gf

docker build . -t dockertest.gf.com.cn/dataportal/dify-api

docker push dockertest.gf.com.cn/dataportal/dify-api

docker tag dockertest.gf.com.cn/dataportal/dify-api docker2.gf.com.cn/dataportal/dify-api:${VERSION}

docker push docker2.gf.com.cn/dataportal/dify-api:${VERSION}