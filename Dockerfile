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

# Collect static files at build time (needs a dummy secret key)
RUN DJANGO_SECRET_KEY=build-placeholder python3 manage.py collectstatic --noinput

# Startup: restore DB from S3, run migrations, seed data, then serve via Daphne (ASGI)
CMD python3 manage.py restore_db || true && \
    python3 manage.py migrate --noinput && \
    python3 manage.py load_initial_data || true && \
    python3 manage.py create_superusers || true && \
    daphne -b 0.0.0.0 -p 8000 southernpark.asgi:application