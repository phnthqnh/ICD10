#!/bin/sh

set -e 

echo "================================ RUNNING MIGRATIONS ======================================"

python manage.py makemigrations
python manage.py makemigrations ICD10

python manage.py migrate --noinput
python manage.py migrate ICD10 --noinput

echo "================================ ✅ DONE MIGRATES ======================================="

python manage.py runserver 0.0.0.0:8000
