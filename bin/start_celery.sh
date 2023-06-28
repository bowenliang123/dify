PROJECT_PATH=$(cd `dirname $0`/..; pwd)
export OPENAI_API_BASE=http://inlps.smart-zone-dev.gf.com.cn/api/llm/internal/chatglm/v1
source /Users/jeanlyn/anaconda3/bin/activate dify

cd $PROJECT_PATH/api
celery -A app.celery worker -P gevent -c 1 --loglevel INFO

