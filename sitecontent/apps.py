from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Content apps whose saves should trigger an S3 backup.
# Excludes 'admin' (LogEntry on every page click) and 'sessions' (every login).
_BACKUP_APPS = frozenset(['sitecontent', 'faculty', 'pages', 'gallery', 'policies', 'auth'])


class SitecontentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sitecontent"
    verbose_name = "Website Administration"

    def ready(self):
        import os
        from django.db.models.signals import post_save, post_delete
        from django.db import connection
        from sitecontent.s3_backup import backup_db

        if not os.environ.get("S3_AWS_STORAGE_BUCKET_NAME") and not settings.DEBUG:
            logger.warning(
                "[sitecontent] No S3 bucket configured — DB/media won't persist across redeploys."
            )

        # Auto-backup: after any content model save/delete, upload SQLite to S3.
        # Fires on every admin Save — no manual action required.
        def backup_on_change(sender, **kwargs):
            if sender._meta.app_label in _BACKUP_APPS:
                try:
                    connection.on_commit(backup_db)
                except Exception as e:
                    logger.error(f"[sitecontent] Failed to schedule S3 backup: {e}")

        post_save.connect(backup_on_change)
        post_delete.connect(backup_on_change)
