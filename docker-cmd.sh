#!/usr/bin/env sh

set -o errexit
set -o nounset

if [ "$APP_MIGRATE" = "on" ]; then
	echo "Apply database migrations"
	python manage.py db migrate
fi

if [ "$START_APP" = "on" ]; then
	echo "Starting server"
	python manage.py start
fi
