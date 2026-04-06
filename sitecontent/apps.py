from django.apps import AppConfig
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
        from sitecontent.s3_backup import restore_db, backup_db

        # Restore DB on startup if on Lightsail/Production and not yet restored
        # We check both environment and a sentinel to prevent double-restores across processes
        has_bucket = "S3_AWS_STORAGE_BUCKET_NAME" in os.environ
        has_not_restored = os.environ.get("DB_RESTORED") != "True"

        if has_bucket and has_not_restored:
            try:
                if restore_db():
                    os.environ["DB_RESTORED"] = "True"
                    logger.info("[sitecontent] Database restored from S3 successfully.")
            except Exception as e:
                logger.error(f"[sitecontent] DB restore failed: {e}")

        def backup_on_change(sender, **kwargs):
            # Only trigger on models within our apps
            managed_apps = ['sitecontent', 'faculty', 'pages', 'gallery', 'policies', 'auth', 'admin', 'sessions']
            if sender._meta.app_label in managed_apps:
                try:
                    connection.on_commit(backup_db)
                except Exception as e:
                    logger.error(f"[sitecontent] Failed to schedule S3 backup: {e}")

        post_save.connect(backup_on_change)
        post_delete.connect(backup_on_change)
