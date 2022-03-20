web: gunicorn irrigation_schedule_recommendor.wsgi:application --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate