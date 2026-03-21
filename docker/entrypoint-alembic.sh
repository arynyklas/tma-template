#!/bin/sh
set -e

echo "Running Alembic migrations..."

exec alembic upgrade head
