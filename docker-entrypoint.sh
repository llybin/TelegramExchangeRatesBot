#!/usr/bin/env sh

set -o errexit
set -o nounset

cmd="$*"

# TODO: get rid hardcode
db_ready() {
	dockerize -wait "tcp://db:5432" -timeout 10s
}

until db_ready; do
	echo >&2 'DB is unavailable - sleeping'
done

echo >&2 'DB is up - continuing...'

# TODO: BROKER_URL

# TODO: get rid hardcode
redis_ready() {
	dockerize -wait "tcp://redis:6379" -timeout 10s
}

until redis_ready; do
	echo >&2 'REDIS is unavailable - sleeping'
done

echo >&2 'REDIS is up - continuing...'

# Evaluating passed command (do not touch):
# shellcheck disable=SC2086
exec $cmd
