# AWS Lightsail Deployment Guide

Step-by-step record of what was done to deploy a Django app to AWS Lightsail via GitHub Actions. Repeat this for any new Django project.

---

## Prerequisites (local machine)

```bash
brew install mysql
pip3 install -r requirements.txt
python3 manage.py runserver  # verify it works locally
```

---

## Step 1 — Add AWS packages to the Django project

**`requirements.txt`** — add:
```
boto3
django-storages
uwsgi
```

**`southernpark/settings.py`** (adapt module name per project):
- Add `"storages"` to `INSTALLED_APPS`
- Add Lightsail to CSRF origins:
```python
_csrf_origins = ["https://localhost", "https://127.0.0.1", "https://*.amazonlightsail.com"]
```
- Add S3 media storage block (only activates when env var is set):
```python
_s3_bucket = os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")
if _s3_bucket:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = _s3_bucket
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
```

---

## Step 2 — Add deployment files

**`Dockerfile`** (project root):
```dockerfile
FROM python:3.10-buster
EXPOSE 8000/tcp
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python3 manage.py migrate --noinput && \
    uwsgi --http 0.0.0.0:8000 \
          --protocol uwsgi \
          --wsgi <project_name>.wsgi:application
```
Replace `<project_name>` with your Django project module (e.g. `southernpark`).

**`AWS/nginx/Dockerfile`**:
```dockerfile
FROM nginx:1.19.0-alpine
RUN mkdir /tmp/nginx
COPY staticfiles/ ./static
COPY staticfiles/ ./staticfiles
COPY AWS/nginx/default.conf ./etc/nginx/conf.d/default.conf
EXPOSE 80
```

**`AWS/nginx/default.conf`**:
```nginx
proxy_cache_path /tmp/nginx keys_zone=mycache:1m;
server {
    client_max_body_size 0;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    location /healthcheck {
        add_header Content-Type text/plain;
        return 200 'Up and running!';
    }
    location /static/ {
        proxy_cache mycache;
        proxy_cache_background_update on;
        proxy_cache_use_stale updating;
        proxy_cache_valid 60s;
        alias /static/;
    }
}
```

**`AWS/deploymentconfig.json`**:
```json
{
  "django": {
    "image": ":djangoapp.django.latest",
    "ports": {"8000": "HTTP"}
  },
  "nginx": {
    "image": ":djangoapp.nginx.latest",
    "ports": {"80": "HTTP"}
  }
}
```

**`AWS/publicendpoint.json`**: copy from the template repo as-is.

---

## Step 3 — GitHub Actions workflow

**`.github/workflows/deploy.yml`** — key points:
- Triggers on push to `main`
- Builds two Docker images: `django` and `nginx`
- Runs `collectstatic` before building nginx (so `staticfiles/` exists)
- Creates a `.env` file from GitHub secrets
- Pushes both images to Lightsail container registry
- Deploys using `AWS/deploymentconfig.json` and `AWS/publicendpoint.json`

**Do NOT** use `sudo pip3 install --upgrade pip` — it fails on debian's system pip. Just use `pip3 install -r requirements.txt`.

---

## Step 4 — AWS setup

1. Go to [lightsail.aws.amazon.com](https://lightsail.aws.amazon.com)
2. Create a **Container Service** named exactly `djangoapp`, pick your region (e.g. `us-east-1`)
3. Go to **IAM → Users → your user → Add permissions → Create inline policy**
4. Use this JSON (no leading spaces):
```json
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"lightsail:*","Resource":"*"}]}
```
5. Name it `LightsailFullAccess` and save

For S3 media storage:
- Create a **Lightsail Storage Bucket**
- Get the `S3_ACCESS_KEY` and `S3_SECRET_KEY` from the bucket's Access keys tab

---

## Step 5 — GitHub repository secrets

Go to **repo → Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | From AWS IAM user |
| `AWS_SECRET_ACCESS_KEY` | From AWS IAM user |
| `AWS_REGION` | Must match Lightsail region (e.g. `us-east-1`) |
| `DJANGO_SECRET_KEY` | Generate: `python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `S3_ACCESS_KEY` | From Lightsail storage bucket |
| `S3_SECRET_KEY` | From Lightsail storage bucket |
| `S3_AWS_STORAGE_BUCKET_NAME` | Your bucket name |

**Persistent storage note**
- If you set `S3_AWS_STORAGE_BUCKET_NAME` along with `S3_ACCESS_KEY` and `S3_SECRET_KEY`, the app will:
  - restore `db.sqlite3` from S3 on startup,
  - backup DB changes to S3 after model saves/deletes,
  - use S3 for uploaded media files in production.
- If you do not set these S3 secrets in production, SQLite and local media will reset on each container redeploy.

---

## Step 6 — Deploy

Push to `main` — GitHub Actions triggers automatically. Watch progress at:
`github.com/<username>/<repo>/actions`

After a successful deploy, Lightsail shows the public URL:
`djangoapp.<id>.<region>.cs.amazonlightsail.com`

Add that domain to `ALLOWED_HOSTS` in `settings.py` if needed.

---

## Notes

- SQLite resets on every container redeploy. Re-create the Django superuser after each deploy: `python3 manage.py createsuperuser`
- To switch to a persistent DB later, add `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` secrets and update `settings.py` to use PostgreSQL
- Estimated cost: ~$7/month for the Nano container service
