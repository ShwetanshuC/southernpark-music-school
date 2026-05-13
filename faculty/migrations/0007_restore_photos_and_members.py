"""
Restore faculty photo paths and re-add members wiped in the May 12 deployment.
Runs automatically during `manage.py migrate`.
"""
from django.db import migrations


# Confirmed correct S3 paths (verified by viewing the actual image files)
PHOTO_FIXES = [
    # (exact name, s3_path)
    ("Keenan Harmon",      "faculty/KHarmon-crop.jpg"),
    ("Dr. Amy Harris",     "faculty/amy.jpg"),     # DB had wrong extension .jpeg
    ("Elaina Palada",      "faculty/elaina.jpg"),  # DB had wrong format .webp
    ("Sharon Stricklin",   "faculty/IMG_20160323_1.jpg"),
    ("Janice Williams",    "faculty/FullSizeRender.jpg"),
    ("Candace Schmitt",    "faculty/IMG_5019.jpg"),
    ("Mark Catoe",         "faculty/8381139954_7a9da58495_z.jpg"),
    ("Dr. Gay Pappin",     "faculty/IMG_0867-crop.jpg"),
]

# Focal points restored from the pre-wipe backup DB
FOCAL_FIXES = [
    # (exact name, focal_y, focal_y_mobile)
    ("Sharon Stricklin",   26, 21),
    ("Janice Williams",    14, 14),
    ("Mark Catoe",         18,  5),
]

# Members whose records were wiped (bios from the May 13 S3 backup)
MISSING_MEMBERS = [
    {
        "name":       "Samantha Roddy",
        "title":      "Instructor of Violin and Viola",
        "instrument": "Violin & Viola",
        "sort_order": 0,
        "bio":        "MM violin performance Indiana University. BMus U of Tennessee. "
                      "Frequently plays with symphonies in North Carolina. "
                      "Has trained teachers using Suzuki method.",
    },
    {
        "name":       "Mario Barragan",
        "title":      "Instructor of Guitar and Ukulele",
        "instrument": "Guitar",
        "sort_order": 0,
        "bio":        "BMus from Queens University. A native of Bogotá, Colombia, "
                      "Mario's musical journey began with playing traditional Colombian music at the age of 14.",
    },
    {
        "name":       "Alexandra Liambos Mura",
        "title":      "Instructor of Voice",
        "instrument": "Voice",
        "sort_order": 12,
        "bio":        "BMus from São Paulo State University. Post-graduate student in Vocal Pedagogy. "
                      "Native of Brazil. Professional performance experience in music theater and opera.",
    },
]


def restore_faculty(apps, schema_editor):
    FacultyMember = apps.get_model("faculty", "FacultyMember")
    Instrument = apps.get_model("faculty", "Instrument")

    # Fix photo paths
    for name, path in PHOTO_FIXES:
        FacultyMember.objects.filter(name=name).update(photo=path)

    # Fix focal points
    for name, fy, fy_m in FOCAL_FIXES:
        FacultyMember.objects.filter(name=name).update(
            image_focal_y=fy,
            image_focal_y_mobile=fy_m,
        )

    # Re-create missing members
    for data in MISSING_MEMBERS:
        if FacultyMember.objects.filter(name=data["name"]).exists():
            continue
        instrument = Instrument.objects.filter(name=data["instrument"]).first()
        FacultyMember.objects.create(
            name=data["name"],
            title=data["title"],
            instrument=instrument,
            sort_order=data["sort_order"],
            bio=data["bio"],
            is_active=True,
            photo="",
            image_focal_y=50,
            image_focal_y_mobile=50,
            image_focal_x_mobile=50,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("faculty", "0006_add_image_focal_x_mobile"),
    ]

    operations = [
        migrations.RunPython(restore_faculty, noop),
    ]
