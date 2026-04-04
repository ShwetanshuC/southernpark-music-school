from django.core.management.base import BaseCommand
from sitecontent.s3_backup import restore_db


class Command(BaseCommand):
    help = "Download db.sqlite3 from S3 (run before migrate on container startup)"

    def handle(self, *args, **options):
        if restore_db():
            self.stdout.write("DB restored from S3.")
        else:
            self.stdout.write("No backup found in S3 — starting with fresh DB.")
