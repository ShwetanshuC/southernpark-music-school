"""
Restore faculty photo paths and re-add members lost in the May 12 deployment wipe.

Run on the production server after deploying:
    python manage.py restore_faculty_photos

For IMG_5529.jpg (Samantha Roddy or Alexandra Liambos Mura):
    python manage.py restore_faculty_photos --img5529 samantha
    python manage.py restore_faculty_photos --img5529 alexandra
"""
from django.core.management.base import BaseCommand
from faculty.models import FacultyMember, Instrument


# S3 paths confirmed by visual verification of the actual image files
PHOTO_FIXES = [
    # (name fragment,             correct S3 path)
    ("Harmon",                    "faculty/KHarmon-crop.jpg"),
    ("Amy Harris",                "faculty/amy.jpg"),       # DB had wrong ext .jpeg
    ("Elaina Palada",             "faculty/elaina.jpg"),    # DB had wrong format .webp
]

# Faculty members whose DB records were wiped and need re-creating if missing.
# Instrument names match faculty_instrument table.
MISSING_MEMBERS = [
    {
        "name":        "Samantha Roddy",
        "title":       "Instructor of Violin and Viola",
        "instrument":  "Violin & Viola",
        "sort_order":  0,
        "bio":         "MM violin performance Indiana University. BMus U of Tennessee. "
                       "Frequently plays with symphonies in North Carolina. "
                       "Has trained teachers using Suzuki method.",
    },
    {
        "name":        "Mario Barragan",
        "title":       "Instructor of Guitar and Ukulele",
        "instrument":  "Guitar",
        "sort_order":  0,
        "bio":         "BMus from Queens University. A native of Bogotá, Colombia, "
                       "Mario's musical journey began with playing traditional Colombian music at the age of 14.",
    },
    {
        "name":        "Alexandra Liambos Mura",
        "title":       "Instructor of Voice",
        "instrument":  "Voice",
        "sort_order":  12,
        "bio":         "BMus from São Paulo State University. Post-graduate student in Vocal Pedagogy. "
                       "Native of Brazil. Professional performance experience in music theater and opera.",
    },
]

# IMG_5529.jpg is a confirmed real photo of one of the two women above.
# Pass --img5529 samantha OR --img5529 alexandra once you've confirmed who it is.
IMG5529_TARGETS = {
    "samantha":  "Samantha Roddy",
    "alexandra": "Alexandra Liambos Mura",
}


class Command(BaseCommand):
    help = "Restore faculty photo paths and re-add members wiped on May 12 deployment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--img5529",
            choices=list(IMG5529_TARGETS.keys()),
            help="Assign IMG_5529.jpg to 'samantha' or 'alexandra' once confirmed",
        )

    def handle(self, *args, **options):
        # ── 1. Fix known broken/missing photo paths ───────────────────────────
        self.stdout.write("\n── Fixing photo paths ──")
        for fragment, path in PHOTO_FIXES:
            qs = FacultyMember.objects.filter(name__icontains=fragment)
            n = qs.update(photo=path)
            if n:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {fragment} → {path}"))
            else:
                self.stdout.write(self.style.WARNING(f"  ! '{fragment}' not found in DB"))

        # ── 2. Assign IMG_5529.jpg if --img5529 was passed ────────────────────
        img5529 = options.get("img5529")
        if img5529:
            target_name = IMG5529_TARGETS[img5529]
            n = FacultyMember.objects.filter(name=target_name).update(
                photo="faculty/IMG_5529.jpg"
            )
            if n:
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ IMG_5529.jpg → {target_name}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"  ! '{target_name}' not found — will be created below"
                ))

        # ── 3. Re-add missing members ─────────────────────────────────────────
        self.stdout.write("\n── Restoring missing faculty members ──")
        for data in MISSING_MEMBERS:
            if FacultyMember.objects.filter(name=data["name"]).exists():
                self.stdout.write(f"  – {data['name']} already exists, skipping")
                continue

            instrument = None
            try:
                instrument = Instrument.objects.get(name=data["instrument"])
            except Instrument.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"  ! Instrument '{data['instrument']}' not found for {data['name']}"
                ))

            photo = ""
            if img5529 and IMG5529_TARGETS.get(img5529) == data["name"]:
                photo = "faculty/IMG_5529.jpg"

            FacultyMember.objects.create(
                name=data["name"],
                title=data["title"],
                instrument=instrument,
                sort_order=data["sort_order"],
                bio=data["bio"],
                is_active=True,
                photo=photo,
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {data['name']}"))

        # ── 4. Summary ────────────────────────────────────────────────────────
        self.stdout.write("\n── Current photo status ──")
        for m in FacultyMember.objects.filter(is_active=True).order_by("sort_order", "name"):
            status = "✓" if m.photo else "✗ MISSING"
            self.stdout.write(f"  {status}  {m.name} ({m.photo or 'no photo'})")

        if not img5529:
            self.stdout.write(self.style.WARNING(
                "\n  IMG_5529.jpg is unassigned. View it, then re-run with:\n"
                "    python manage.py restore_faculty_photos --img5529 samantha\n"
                "    python manage.py restore_faculty_photos --img5529 alexandra"
            ))
