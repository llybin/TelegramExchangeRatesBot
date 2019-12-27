#!/usr/bin/env bash

echo "Compile locales"
pybabel compile -d locale

echo "Apply database migrations"
./manage.py db migrate

echo "Start server"
./manage.py start
