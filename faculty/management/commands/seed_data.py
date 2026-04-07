"""
Seed initial data: SiteSettings, HeroSlides, FacultyMembers, PolicySections, GalleryPhotos.
"""
from __future__ import annotations

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from sitecontent.models import HeroSlide, SiteSettings
from faculty.models import FacultyMember, Instrument
from gallery.models import GalleryPhoto
from policies.models import PolicySection


FACULTY_DATA = [
    {
        "name": "Dr. Michael Lehtinen",
        "title": "School Director",
        "instrument_tag": "piano",
        "photo": "michael.jpg",
        "bio": (
            "DMA and MM from the Eastman School of Music; BMUs from Oberlin Conservatory. "
            "Director since 2006, teaching at Southern Park since 1995. His students participate "
            "in festivals and competitions throughout Charlotte and NC. He is also the Organist "
            "at St. Stephen United Methodist Church."
        ),
        "sort_order": 10,
    },
    {
        "name": "Dr. Amy Harris",
        "title": "Instructor of Piano",
        "instrument_tag": "piano",
        "photo": "amy.jpeg",
        "bio": (
            "DMA from UNC Greensboro; MM and BMus from University of Georgia. Teaching private "
            "piano in Charlotte since 2005. Nationally Certified Teacher of Music, Registered "
            "Suzuki Piano Teacher, member of MTNA and the Charlotte Piano Teachers Forum."
        ),
        "sort_order": 20,
    },
    {
        "name": "Sharon Stricklin",
        "title": "Instructor of Piano",
        "instrument_tag": "piano",
        "photo": "stricklin.jpeg",
        "bio": (
            "MM and BMus from Michigan State University. 40 years of piano teaching experience. "
            "Previously taught middle and high school choral music, AP Music Theory, and AP Music "
            "History. Former church music director and accompanist."
        ),
        "sort_order": 30,
    },
    {
        "name": "Dr. Gregory Thompson",
        "title": "Instructor of Piano",
        "instrument_tag": "piano",
        "photo": "gregory.avif",
        "bio": (
            "DMA from University of South Carolina. Recitalist and collaborative pianist with "
            "performances in the U.S., Europe, and Asia. He enjoys sharing his love of the piano "
            "with students of all ages and abilities."
        ),
        "sort_order": 40,
    },
    {
        "name": "Janice Williams",
        "title": "Instructor of Piano & Voice",
        "instrument_tag": "piano voice",
        "photo": "teacher1.jpeg",
        "bio": (
            "MM from St. Louis Conservatory of Music; BMus from Tulsa University. Over 20 years "
            "teaching experience. Performed with Opera Carolina for 12 years. Also sings regularly "
            'at Charlotte-area churches and performs with the "In The Mood" trio.'
        ),
        "sort_order": 50,
    },
    {
        "name": "Marscia Martinez-Mendoza",
        "title": "Instructor of Violin & Viola",
        "instrument_tag": "violin viola",
        "photo": "violin.png",
        "bio": "Instructor of Violin & Viola at Southern Park Music School.",
        "sort_order": 60,
    },
    {
        "name": "Alasondro Linney",
        "title": "Instructor of Violin & Viola",
        "instrument_tag": "violin viola",
        "photo": "violin.png",
        "bio": (
            "BMus from NC School of the Arts. Teaches both traditional and Suzuki method. "
            "Has performed with the Charlotte Symphony and Alabama Symphony, and enjoys sharing "
            "that experience with his students."
        ),
        "sort_order": 70,
    },
    {
        "name": "Andrew Werner",
        "title": "Instructor of Cello",
        "instrument_tag": "cello",
        "photo": "cello.png",
        "bio": "Andrew has a BMus in Cello Performance from James Madison University.",
        "sort_order": 80,
    },
    {
        "name": "Elaina Palada",
        "title": "Instructor of Flute",
        "instrument_tag": "flute",
        "photo": "elaina.webp",
        "bio": (
            "MM from Northwestern University; BM from Syracuse University. Moved to Charlotte in "
            "2022 to work for Flute World. Active performer and substitute flutist for multiple "
            "regional orchestras. Five+ years teaching flute to all ages."
        ),
        "sort_order": 90,
    },
    {
        "name": "Candace Schmitt",
        "title": "Instructor of Oboe",
        "instrument_tag": "oboe flute",
        "photo": "flute.png",
        "bio": (
            "BA from UNC Charlotte; BM from Appalachian State University. Plays oboe, flute, and "
            "English horn. Adjunct Instructor at Gardner-Webb University. Performs with the "
            "Charlotte Civic Orchestra and Charlotte Flute Choir."
        ),
        "sort_order": 100,
    },
    {
        "name": "Mark Catoe",
        "title": "Instructor of Saxophone & Clarinet",
        "instrument_tag": "saxophone clarinet",
        "photo": "saxophone.png",
        "bio": (
            "BMusEd from Winthrop University. Multi-instrumentalist with six+ years performing in "
            "the area, including two years on a cruise ship. Notable performances with the "
            "Charlotte Symphony, The Temptations, and The Four Tops. Also performs as a jazz pianist."
        ),
        "sort_order": 110,
    },
    {
        "name": "Dr. Gay Pappin",
        "title": "Administrative Assistant",
        "instrument_tag": "administrator",
        "photo": "gay.jpeg",
        "bio": (
            "DMA and MM from Louisiana State University; BMusEd from Ouachita Baptist University. "
            "Has taught piano, organ, theory, and music appreciation at several universities. "
            "Church pianist and organist for most of her life. Loves working with Southern Park families."
        ),
        "sort_order": 200,
    },
]

POLICY_DATA = [
    {
        "title": "Summer 2025 Term",
        "body": (
            "<p>Tuesday, June 3 – Sunday, August 17, 2025<br>"
            "Summer Term fees are based upon the number of lessons scheduled by mutual agreement "
            "of the teacher and student/parent. The Summer Term administrative fee is $26 with a "
            "sibling discount of $13.</p>"
        ),
        "sort_order": 10,
    },
    {
        "title": "Fall 2025 Term",
        "body": (
            "<p>Monday, August 18, 2025 – January 11, 2026<br>"
            "18 30-minute lessons ($38/lesson): <strong>$722</strong><br>"
            "18 45-minute lessons ($57/lesson): <strong>$1,064</strong><br>"
            "18 60-minute lessons ($76/lesson): <strong>$1,406</strong><br>"
            "<em>(includes a non-refundable $38 administrative fee)</em></p>"
        ),
        "sort_order": 20,
    },
    {
        "title": "Fall & Spring Terms",
        "body": (
            "<p>Students take one lesson per week. During the fall and spring, Southern Park Music "
            "School operates on a <strong>term basis</strong>; however, if a student enters "
            "mid-term, the fee will be <strong>prorated</strong> to reflect the number of weeks "
            "remaining in the term. Invoices may be paid with cash or check. "
            "<strong>We do not accept credit cards.</strong><br><br>"
            "<strong>Fees are due before the first lesson of the term.</strong> Any exceptions "
            "must be discussed with the Director. A $35 fee will be assessed for a returned check.</p>"
        ),
        "sort_order": 30,
    },
    {
        "title": "Interview Lessons",
        "body": (
            "<p>Students may request a 30-minute interview lesson for a charge of $38. Payment is "
            "due at the time of the lesson by check or cash. <strong>We do not accept credit cards. "
            "An interview lesson may not be rescheduled or refunded.</strong></p>"
        ),
        "sort_order": 40,
    },
    {
        "title": "Banked Time",
        "body": "<p>Any extra time given by a teacher may be used for an absence.</p>",
        "sort_order": 50,
    },
    {
        "title": "Instruction for All Ages",
        "body": (
            "<p>Southern Park Music School offers music instruction to students of "
            "<strong>all ages and abilities</strong>.</p>"
        ),
        "sort_order": 60,
    },
    {
        "title": "Missed Lessons",
        "body": (
            "<p><strong>The teacher is under no obligation to make up lessons missed by the "
            "student.</strong> Lessons postponed by the teacher will be made up before the end of "
            "the term. If a teacher has scheduled a make-up lesson and the student is absent, the "
            "teacher is under no further obligation to reschedule.</p>"
        ),
        "sort_order": 70,
    },
    {
        "title": "Bad Weather",
        "body": (
            "<p>Southern Park Music School <strong>will not cancel lessons due to dangerous "
            "weather</strong>. If a particular teacher must reschedule lessons due to severe "
            "weather, lessons will be made up according to the above guidelines. In the event of "
            "adverse weather, please contact your teacher individually to arrange a virtual lesson.</p>"
        ),
        "sort_order": 80,
    },
    {
        "title": "Performances",
        "body": (
            "<p>Student performances play an important part in the development of a good musician. "
            "<strong>We encourage all students to participate in recitals, festivals, and "
            "contests.</strong> During the fall and spring terms, recitals are scheduled on certain "
            "Sundays at 2:30 p.m; mandatory dress rehearsals are Saturday at 2:30 p.m. Times may vary.</p>"
        ),
        "sort_order": 90,
    },
    {
        "title": "Photography & Videography",
        "body": (
            "<p>Individuals may make audio/video recordings of their own relatives in recitals. "
            "Individuals may not make images of non-family members.</p>"
        ),
        "sort_order": 100,
    },
    {
        "title": "Refund Policy",
        "body": "<p><strong>No refunds will be made for early withdrawal.</strong></p>",
        "sort_order": 110,
    },
]

GALLERY_PHOTOS = [
    ("gallery1.jpg", "", 10),
    ("gallery2.jpg", "", 20),
    ("gallery3.jpg", "", 30),
    ("gallery4.jpg", "", 40),
    ("gallery5.jpg", "", 50),
    ("gallery6.jpg", "", 60),
    ("gallery7.jpg", "", 70),
    ("gallery8.jpg", "", 80),
]

HERO_SLIDES = [
    ("carnegie.jpeg", "Carnegie Hall performance", 10),
    ("gallery1.jpg", "Student recital", 20),
    ("gallery2.jpg", "Student recital", 30),
]

CALENDAR_EMBED_URL = (
    "https://calendar.google.com/calendar/embed"
    "?src=c_45cc094f4ecc9abdcf76aeec72e0ec7827f2afec4cdfbaee569121134630aa76"
    "%40group.calendar.google.com&ctz=America%2FNew_York"
)


def _sync_image(instance, field_name, src_path, filename):
    """Re-save a file field from src_path if the file is missing on disk."""
    field = getattr(instance, field_name)
    if field and field.storage.exists(field.name):
        return False  # already on disk
    if not src_path.exists():
        return False
    with open(src_path, "rb") as f:
        field.save(filename, File(f), save=True)
    return True


class Command(BaseCommand):
    help = "Seed initial data for Southern Park Music School"

    def handle(self, *args, **options):
        images_dir = settings.BASE_DIR / "static" / "images"

        # SiteSettings — create if missing, always ensure calendar URL is set
        site, created = SiteSettings.objects.get_or_create(pk=1)
        if created:
            self.stdout.write(self.style.SUCCESS("Created SiteSettings"))
        if not site.calendar_embed_url:
            site.calendar_embed_url = CALENDAR_EMBED_URL
            site.save(update_fields=["calendar_embed_url"])
            self.stdout.write(self.style.SUCCESS("Set calendar embed URL"))

        # HeroSlides
        if not HeroSlide.objects.exists():
            for filename, alt, order in HERO_SLIDES:
                slide = HeroSlide(alt=alt, sort_order=order)
                img_path = images_dir / filename
                if img_path.exists():
                    with open(img_path, "rb") as f:
                        slide.image.save(filename, File(f), save=False)
                slide.save()
            self.stdout.write(self.style.SUCCESS(f"Created {len(HERO_SLIDES)} hero slides"))
        else:
            synced = sum(
                1 for s in HeroSlide.objects.filter(image__isnull=False)
                if s.image and _sync_image(s, "image", images_dir / s.image.name.split("/")[-1], s.image.name.split("/")[-1])
            )
            if synced:
                self.stdout.write(self.style.SUCCESS(f"Re-synced {synced} hero slide images"))

        # Faculty
        if not FacultyMember.objects.exists():
            for data in FACULTY_DATA:
                data = dict(data)  # don't mutate the module-level list
                photo_filename = data.pop("photo")
                slug = data.pop("instrument_tag", "")
                instrument = Instrument.objects.filter(slug=slug).first() if slug else None
                member = FacultyMember(instrument=instrument, **data)
                img_path = images_dir / photo_filename
                if img_path.exists():
                    try:
                        with open(img_path, "rb") as f:
                            member.photo.save(photo_filename, File(f), save=False)
                    except Exception as e:
                        self.stdout.write(f"  Warning: could not attach {photo_filename}: {e}")
                member.save()
            self.stdout.write(self.style.SUCCESS(f"Created {len(FACULTY_DATA)} faculty members"))
        else:
            # Re-sync any photos missing from disk (e.g. after volume remount)
            name_to_file = {d["name"]: d["photo"] for d in FACULTY_DATA}
            synced = 0
            for member in FacultyMember.objects.all():
                photo_filename = name_to_file.get(member.name)
                if photo_filename:
                    src = images_dir / photo_filename
                    if member.photo:
                        if _sync_image(member, "photo", src, photo_filename):
                            synced += 1
                    elif src.exists():
                        with open(src, "rb") as f:
                            member.photo.save(photo_filename, File(f), save=True)
                        synced += 1
            if synced:
                self.stdout.write(self.style.SUCCESS(f"Re-synced {synced} faculty photos"))
            else:
                self.stdout.write("Faculty photos up to date.")

        # PolicySections
        if not PolicySection.objects.exists():
            for data in POLICY_DATA:
                PolicySection.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"Created {len(POLICY_DATA)} policy sections"))

        # Gallery
        if not GalleryPhoto.objects.exists():
            created = 0
            for filename, caption, order in GALLERY_PHOTOS:
                img_path = images_dir / filename
                if img_path.exists():
                    photo = GalleryPhoto(caption=caption, sort_order=order)
                    with open(img_path, "rb") as f:
                        photo.image.save(filename, File(f), save=False)
                    photo.save()
                    created += 1
                else:
                    self.stdout.write(f"  Skipping {filename} (not found)")
            self.stdout.write(self.style.SUCCESS(f"Created {created} gallery photos"))
        else:
            # Re-sync missing gallery images
            file_map = {fn: (fn, cap, ord_) for fn, cap, ord_ in GALLERY_PHOTOS}
            synced = 0
            for photo in GalleryPhoto.objects.all():
                if photo.image:
                    fname = photo.image.name.split("/")[-1]
                    if _sync_image(photo, "image", images_dir / fname, fname):
                        synced += 1
            if synced:
                self.stdout.write(self.style.SUCCESS(f"Re-synced {synced} gallery images"))
            else:
                self.stdout.write("Gallery images up to date.")

        self.stdout.write(self.style.SUCCESS("Seed complete!"))
