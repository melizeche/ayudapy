#!/bin/sh
set -e

shift
cmd="$@"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U $POSTGRES_USER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
