from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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

        # Wire auto-backup: after every committed DB write, upload SQLite to S3 asynchronously
        def backup_on_change(sender, **kwargs):
            managed_apps = ['sitecontent', 'faculty', 'pages', 'gallery', 'policies', 'auth', 'admin', 'sessions']
            if sender._meta.app_label in managed_apps:
                try:
                    connection.on_commit(backup_db)
                except Exception as e:
                    logger.error(f"[sitecontent] Failed to schedule S3 backup: {e}")

        post_save.connect(backup_on_change)
        post_delete.connect(backup_on_change)
