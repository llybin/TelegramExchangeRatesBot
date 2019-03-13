#!/bin/bash

echo "Compile locales"
pybabel compile -d locale

echo "Apply database migrations"
./manage.py db migrate

echo "Starting server"
./manage.py start
