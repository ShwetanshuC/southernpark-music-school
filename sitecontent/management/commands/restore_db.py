from pathlib import Path
from django.core.management import call_command
from django.core.management.base import BaseCommand
from sitecontent.s3_backup import restore_db

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "initial_data.json"


class Command(BaseCommand):
    help = "Restore DB from S3 backup, falling back to bundled fixture"

    def handle(self, *args, **options):
        if restore_db():
            self.stdout.write("DB restored from S3.")
            return

        self.stdout.write("No S3 backup found — loading bundled fixture.")
        if FIXTURE.exists():
            call_command("loaddata", str(FIXTURE), verbosity=1)
            self.stdout.write("Fixture loaded.")
        else:
            self.stdout.write("No fixture found — starting with empty DB.")
