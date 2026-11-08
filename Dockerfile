FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    WEB_CONCURRENCY=3 \
    GUNICORN_CMD_ARGS="--max-requests 1200 " \
    DJANGO_SETTINGS_MODULE=tomd.settings.production

# slim has no curl: build-tailwind.sh needs it, as would a Coolify health check
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /code/
WORKDIR /code/

# Build Tailwind CSS
RUN ./build-tailwind.sh

# Collect static files
RUN python manage.py collectstatic --noinput

RUN useradd --create-home app
USER app

CMD ["./run.sh"]
