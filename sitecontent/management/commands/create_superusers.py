from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


SUPERUSERS = [
    {"username": "shwetanshu", "email": "shwetanshu.c@gmail.com"},
    {"username": "michael",    "email": "director@southernparkmusicschool.com"},
    {"username": "gay",        "email": ""},
]

PASSWORD = "password123"


class Command(BaseCommand):
    help = "Create default superusers if they do not exist"

    def handle(self, *args, **options):
        for u in SUPERUSERS:
            if not User.objects.filter(username__iexact=u["username"]).exists():
                User.objects.create_superuser(
                    username=u["username"],
                    email=u["email"],
                    password=PASSWORD,
                )
                self.stdout.write(f"Created superuser: {u['username']}")
            else:
                self.stdout.write(f"Superuser already exists: {u['username']}")
