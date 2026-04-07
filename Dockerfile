# Set base image (host OS) - using slim variant with current Debian for security
FROM python:3.10-slim

# By default, listen on port
EXPOSE 8000/tcp
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the dependencies file to the working directory
WORKDIR /app

# Install build dependencies for Twisted http2/tls extras and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt .

# Install Python dependencies with pip cache optimization
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Collect static files at build time (needs a dummy secret key)
RUN DJANGO_SECRET_KEY=build-placeholder python3 manage.py collectstatic --noinput

# Startup: restore DB from S3, run migrations, seed data, then serve via gunicorn
CMD ["sh", "-c", "\
  python3 manage.py restore_db || true && \
  python3 manage.py migrate --noinput && \
  python3 manage.py load_initial_data || true && \
  python3 manage.py create_superusers || true && \
  python3 manage.py sync_media || true && \
  trap 'echo \"[startup] SIGTERM received — backing up DB before shutdown\" && python3 manage.py backup_db && exit 0' TERM INT && \
  gunicorn southernpark.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 300 --keep-alive 5 --log-level info & \
  wait $!"]