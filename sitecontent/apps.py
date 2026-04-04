from django.apps import AppConfig


class SitecontentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sitecontent"

    def ready(self):
        from django.db.models.signals import post_save
        from django.db import connection

        def backup_on_save(sender, **kwargs):
            from sitecontent.s3_backup import backup_db
            connection.on_commit(backup_db)

        post_save.connect(backup_on_save)
