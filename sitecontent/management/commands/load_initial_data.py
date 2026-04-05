from pathlib import Path
from django.core.management import call_command
from django.core.management.base import BaseCommand

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "initial_data.json"


class Command(BaseCommand):
    help = "Load fixture into an empty DB (skips if data already exists)"

    def handle(self, *args, **options):
        from sitecontent.models import SiteSettings
        if SiteSettings.objects.exists():
            self.stdout.write("Data already present — skipping fixture load.")
            return
        if FIXTURE.exists():
            call_command("loaddata", str(FIXTURE), verbosity=1)
            self.stdout.write("Fixture loaded.")
        else:
            self.stdout.write("No fixture found.")
