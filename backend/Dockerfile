FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

WORKDIR /app

RUN pip install gunicorn

COPY /backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /backend .
COPY /data ./data/
# COPY /backend/media/ ./media/

CMD ["sh", "-c", "python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py load_data --type ingredients && \
    python manage.py load_data --type users && \
    python manage.py load_data --type recipes && \
    python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 backend.wsgi"]