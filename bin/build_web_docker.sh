PROJECT_PATH=$(cd `dirname $0`/..; pwd)

cd $PROJECT_PATH/web

docker build . -t dockertest.gf.com.cn/dataportal/dify-web

docker push dockertest.gf.com.cn/dataportal/dify-web
