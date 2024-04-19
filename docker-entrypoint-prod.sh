#!/bin/bash

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for mysql..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "MySQL started"
fi

# echo "Clear entire database"
# python manage.py flush --no-input

echo "Appling database migrations..."
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py makemigrations 
python manage.py migrate
python manage.py createcachetable
python manage.py createdefaultdata
python -m gunicorn app.asgi:application -k uvicorn.workers.UvicornWorker
