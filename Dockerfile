FROM python:3.12

ENV PYTHONUNBUFFERED 1 \
    WEB_CONCURRENCY=3 \
    GUNICORN_CMD_ARGS="--max-requests 1200 " \
    DJANGO_SETTINGS_MODULE=tomd.settings.production

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
RUN pip install gunicorn

COPY . /code/
WORKDIR /code/

# Build Tailwind CSS
RUN chmod +x build-tailwind.sh && ./build-tailwind.sh

# Collect static files
RUN python manage.py collectstatic --noinput

CMD ["./run.sh"]
