from django.apps import AppConfig

class SitecontentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sitecontent"
    verbose_name = "Website Administration"

    def ready(self):
        import os
        from django.db.models.signals import post_save, post_delete
        from django.db import connection
        from sitecontent.s3_backup import restore_db, backup_db

        # Restore DB on startup if on Lightsail/Production
        if os.environ.get("S3_AWS_STORAGE_BUCKET_NAME") and not os.environ.get("DB_RESTORED"):
            if restore_db():
                os.environ["DB_RESTORED"] = "True"
                print("[sitecontent] Database restored from S3 successfully.")

        def backup_on_change(sender, **kwargs):
            # Only trigger on models within our apps
            managed_apps = ['sitecontent', 'faculty', 'pages', 'gallery', 'policies', 'auth', 'admin', 'sessions']
            if sender._meta.app_label in managed_apps:
                connection.on_commit(backup_db)

        post_save.connect(backup_on_change)
        post_delete.connect(backup_on_change)
