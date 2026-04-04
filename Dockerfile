# Set base image (host OS)
FROM python:3.10-buster

# By default, listen on port
EXPOSE 8000/tcp
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the dependencies file to the working directory
WORKDIR /app

COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Startup: load env, run DB setup, then serve
CMD set -a && [ -f .env ] && . ./.env || true; set +a && \
    python3 manage.py restore_db || true && \
    python3 manage.py migrate --noinput || true && \
    python3 manage.py create_superusers || true && \
    uwsgi --http 0.0.0.0:8000 --master --wsgi southernpark.wsgi:application