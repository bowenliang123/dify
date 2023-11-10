PROJECT_PATH=$(cd `dirname $0`/..; pwd)

cd $PROJECT_PATH/web

VERSION=0.3.6-gf

docker build . -t dockertest.gf.com.cn/dataportal/dify-web

docker push dockertest.gf.com.cn/dataportal/dify-web

docker tag dockertest.gf.com.cn/dataportal/dify-web docker2.gf.com.cn/dataportal/dify-web:${VERSION}
docker push docker2.gf.com.cn/dataportal/dify-web:${VERSION}