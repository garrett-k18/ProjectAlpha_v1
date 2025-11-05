release: python manage.py migrate --noinput
web: gunicorn projectalphav1.wsgi:application --bind 0.0.0.0:$PORT




