import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "southernpark.settings")
application = get_wsgi_application()

try:
    # Check if we're dealing with sqlite and should sync
    # We only do this if DATABASE_URL is not set (meaning we are using local sqlite)
    if not os.environ.get("DATABASE_URL") and not os.environ.get("DB_NAME"):
        from sitecontent.s3_backup import restore_db
        restore_db()
except ImportError:
    pass
