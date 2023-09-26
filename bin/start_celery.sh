PROJECT_PATH=$(cd `dirname $0`/..; pwd)
export OPENAI_API_BASE=http://inlps.smart-zone-dev.gf.com.cn/api/llm/v1
export STORAGE_TYPE=s3
export S3_ENDPOINT=http://s3testv6.gf.com.cn:8080
export S3_BUCKET_NAME=gfgpt
export S3_ACCESS_KEY=A5ONZA0MOTBYOCC3CXCI
export S3_SECRET_KEY=EJKSK0v1mq3tmdhhvK132rN3DrAazgPCHYjZZfxo
export S3_REGION=s3testv6

source /Users/jeanlyn/anaconda3/bin/activate dify

cd $PROJECT_PATH/api
celery -A app.celery worker -P gevent -c 1 --loglevel INFO

