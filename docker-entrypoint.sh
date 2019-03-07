#!/bin/bash

echo "Apply database migrations"
./manage.py db migrate

echo "Starting server"
./manage.py start
