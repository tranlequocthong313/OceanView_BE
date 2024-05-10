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
python3 manage.py makemigrations 
python3 manage.py migrate
python3 manage.py createcachetable
python3 manage.py createdefaultdata
python3 manage.py crontab remove
python3 manage.py crontab add
python manage.py crontab show
python3 manage.py runserver 0.0.0.0:8000

