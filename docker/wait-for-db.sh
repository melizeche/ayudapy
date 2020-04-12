#!/bin/sh
set -e

shift
cmd="$@"

until PGPASSWORD=$SECRET_KEY psql -h "db" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
