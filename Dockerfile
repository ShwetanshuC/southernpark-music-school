# Set base image (host OS)
FROM python:3.10-buster

# By default, listen on port
EXPOSE 8000/tcp
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .
# Run migrations then start server
CMD python3 manage.py migrate --noinput && \
    python3 manage.py create_superusers && \
    uwsgi --http 0.0.0.0:8000 \
          --protocol uwsgi \
          --wsgi southernpark.wsgi:application