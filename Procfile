release: cd projectalphav1 && python manage.py migrate --noinput
web: cd projectalphav1 && gunicorn projectalphav1.wsgi:application --bind 0.0.0.0:$PORT




