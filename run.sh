CMD="uvicorn iwdsync.asgi:application"
[[ "$@" ]] && CMD=$@
source ./.venv/bin/activate

ENV_FILE="./.env.$1"
if [ -f $ENV_FILE ]; then
  echo "Running with $ENV_FILE"
  export $(grep -v '^#' $ENV_FILE | xargs)
fi

$CMD
