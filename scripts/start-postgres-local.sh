#!/usr/bin/env bash

set -euo pipefail

CONTAINER_NAME="cofrap-postgres"
POSTGRES_IMAGE="postgres:15"
POSTGRES_DB="cofrapdb"
POSTGRES_USER="cofrap"
POSTGRES_PASSWORD="cofrap2024"
HOST_PORT="5432"
SQL_FILE="infra/db/init.sql"

if ! command -v docker >/dev/null 2>&1; then
  echo "MISSING docker: please install Docker before running this script."
  exit 1
fi

if [ ! -f "$SQL_FILE" ]; then
  echo "Missing SQL file: $SQL_FILE"
  exit 1
fi

container_exists() {
  docker ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"
}

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"
}

echo "Starting local PostgreSQL container..."

if container_running; then
  echo "Container $CONTAINER_NAME is already running."
elif container_exists; then
  echo "Container $CONTAINER_NAME exists but is stopped. Restarting it..."
  docker start "$CONTAINER_NAME" >/dev/null
else
  echo "Creating container $CONTAINER_NAME with image $POSTGRES_IMAGE..."
  docker run -d \
    --name "$CONTAINER_NAME" \
    -e POSTGRES_DB="$POSTGRES_DB" \
    -e POSTGRES_USER="$POSTGRES_USER" \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -p "$HOST_PORT:5432" \
    "$POSTGRES_IMAGE" >/dev/null
fi

echo "Waiting for PostgreSQL to be ready..."
for attempt in $(seq 1 30); do
  if docker exec "$CONTAINER_NAME" pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; then
    break
  fi

  if [ "$attempt" -eq 30 ]; then
    echo "PostgreSQL is not ready after 30 seconds."
    exit 1
  fi

  sleep 1
done

echo "Applying database schema from $SQL_FILE..."
docker cp "$SQL_FILE" "$CONTAINER_NAME:/tmp/init.sql"
docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /tmp/init.sql

echo
echo "PostgreSQL local is ready."
echo "Container: $CONTAINER_NAME"
echo "Database:  $POSTGRES_DB"
echo "User:      $POSTGRES_USER"
echo "Port:      $HOST_PORT"
echo
echo "Connect with:"
echo "docker exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB"
