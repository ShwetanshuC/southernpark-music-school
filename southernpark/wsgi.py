import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "southernpark.settings")
application = get_wsgi_application()

# Fallback: Restore DB from S3 if not already done by AppConfig.ready()
# Only runs once per process if S3 credentials are present
if os.environ.get("S3_AWS_STORAGE_BUCKET_NAME") and not os.environ.get("DB_RESTORED"):
    try:
        from sitecontent.s3_backup import restore_db
        if restore_db():
            os.environ["DB_RESTORED"] = "True"
    except Exception:
        pass

