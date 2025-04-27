FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

WORKDIR /app

RUN pip install gunicorn

COPY /backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /backend .
COPY /data/ingredients.json .
COPY /data/users.json .
COPY /data/recipes.json .
# COPY /backend/media/ /app/media/

CMD ["sh", "-c", "python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py load_ingredients && \
    python manage.py load_users && \
    python manage.py load_recipes && \
    python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 backend.wsgi"]