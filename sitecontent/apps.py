from django.apps import AppConfig

class SitecontentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sitecontent"
    verbose_name = "Website Administration"

    def ready(self):
        from django.db.models.signals import post_save, post_delete
        from django.db import connection

        def backup_on_change(sender, **kwargs):
            from sitecontent.s3_backup import backup_db
            # Only trigger on models within our apps
            if sender._meta.app_label in ['sitecontent', 'faculty', 'auth', 'admin', 'sessions']:
                connection.on_commit(backup_db)

        post_save.connect(backup_on_change)
        post_delete.connect(backup_on_change)
