#!/usr/bin/env bash

set -euo pipefail

CONTAINER_NAME="cofrap-postgres"

if ! command -v docker >/dev/null 2>&1; then
  echo "MISSING docker: please install Docker before running this script."
  exit 1
fi

if docker ps --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
  docker stop "$CONTAINER_NAME" >/dev/null
  echo "Container $CONTAINER_NAME stopped."
elif docker ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
  echo "Container $CONTAINER_NAME already exists but is not running."
else
  echo "Container $CONTAINER_NAME does not exist."
fi
