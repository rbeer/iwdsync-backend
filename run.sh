CMD="uvicorn iwdsync.asgi:application"
[[ "$@" ]] && CMD=$@
source ./.venv/bin/activate
DB_NAME=iwdsync DB_HOST=172.17.0.2 DB_PORT=5432 DB_USER=postgres DB_PASS=IWDSYNC $CMD
