from django.core.management.base import BaseCommand
from faculty.models import FacultyMember


class Command(BaseCommand):
    help = "Restore Keenan Harmon's photo path (S3 file faculty/KHarmon-crop.jpg already exists)"

    def handle(self, *args, **options):
        updated = FacultyMember.objects.filter(name__icontains="Harmon").update(
            photo="faculty/KHarmon-crop.jpg"
        )
        if updated:
            self.stdout.write(self.style.SUCCESS(
                f"Restored photo for {updated} record(s) matching 'Harmon'."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "No faculty member matching 'Harmon' found."
            ))
