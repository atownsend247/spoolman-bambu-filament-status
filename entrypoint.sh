#!/bin/sh



echo $(pwd)

echo $(printenv)

export $(grep -v '^#' .env | xargs)


echo $(pwd)

echo $(printenv)


PUID=${PUID:-1000}
PGID=${PGID:-1000}
SPOOLMAN_BAMBU_PORT=${SPOOLMAN_BAMBU_PORT:-8000}
SPOOLMAN_BAMBU_HOST=${SPOOLMAN_BAMBU_HOST:-0.0.0.0}

groupmod -o -g "$PGID" app
usermod -o -u "$PUID" app

echo User UID: $(id -u app)
echo User GID: $(id -g app)

echo "Starting uvicorn..."

# Execute the uvicorn command with any additional arguments
exec su-exec "app" uvicorn spoolman_bambu.main:app --host $SPOOLMAN_BAMBU_HOST --port $SPOOLMAN_BAMBU_PORT "$@"
