# LSS API server

## Run server

python manage.py runserver 0.0.0.0:8000  
gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5
