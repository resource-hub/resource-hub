#!/bin/sh
ENV=src/resource_hub/settings/prod_env.py

echo SQL_ENGINE=django.db.backends.postgresql_psycopg2 >> ENV

echo SECRET_KEY=$SECRET_KEY >> ENV
echo DB_NAME=$DB_NAME >> ENV
echo DB_USER=$DB_USER >> ENV
echo DB_PW=$DB_PW >> ENV
echo DB_HOST=$DB_HOST >> ENV
echo DB_PORT=$DB_PORT >> ENV