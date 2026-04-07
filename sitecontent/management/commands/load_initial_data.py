from django.core.management.base import BaseCommand
from sitecontent.models import SiteSettings, HomeSection, HomeStat, HomeFeature, HomeHistoryItem

class Command(BaseCommand):
    help = "Seed initial site content — only runs if the DB is empty (skips if data already exists)"

    def handle(self, *args, **options):
        # Skip entirely if any user data already exists (restored from S3 backup)
        if SiteSettings.objects.exists():
            self.stdout.write("Data already exists — skipping initial data load.")
            return

        # 1. SiteSettings
        SiteSettings.objects.create(
            id=1,
            hero_headline="Where the Good<br><em>Become Great</em>",
            hero_subtitle="Private music lessons for all ages — inspiring students for over 60 years",
            phone_display="(704) 676-1002",
            phone_tel="+17046761002",
            email="info@southernparkmusicschool.com",
            address="4805 Park Rd STE 230, Charlotte, NC 28209",
        )

        # 2. About Us
        about_text = (
            "Welcome to Southern Park Music School, where creativity and excellence meet. Our mission is to inspire students "
            "of all ages and abilities through personalised lessons, dynamic ensemble experiences, and immersive performance opportunities.\n\n"
            "Whether you're discovering music for the first time or preparing for a professional career, our dedicated faculty "
            "are here to guide you every step of the way. We offer instruction across a wide range of instruments and musical styles — "
            "in a supportive, welcoming community."
        )
        HomeSection.objects.create(section_type='about', title='About Us', description=about_text)
        HomeSection.objects.create(section_type='why_us', title='Why Choose Southern Park?',
            description="Since 1964, we've helped Charlotte families discover the joy of music with inspiring teachers, a welcoming community, and spaces built for sound.")
        HomeSection.objects.create(section_type='history', title='Our History')

        # 3. Stats
        for num, label, order in [
            ('60', 'Years of Excellence', 0),
            ('8', 'Private Studios', 1),
            ('10', 'Instruments Taught', 2),
            ('Monthly', 'Student Recitals', 3),
        ]:
            HomeStat.objects.create(number=num, label=label, sort_order=order)

        # 4. Features
        for title, text, order in [
            ('Recitals that Inspire', 'We host student performances about once a month during the school year — recitals are always free for performers and their guests.', 0),
            ('Studios Built for Sound', 'Eight private studios, each with an acoustic piano. Every piano lesson is taught on a grand piano for the best feel and tone.', 1),
            ('Exceptional Faculty', 'Experienced performers and educators — many holding advanced music degrees — with a genuine passion for teaching every student.', 2),
            ('Student Success', 'Our students thrive in festivals and competitions, earn awards, and develop a lifelong love of music that extends well beyond lessons.', 3),
        ]:
            HomeFeature.objects.create(title=title, text=text, sort_order=order)

        # 5. History timeline
        for year, desc, order in [
            ('1964', 'Founded by John Whitaker and Harold Nave, Southern Park Music School opened its doors near Park Road Shopping Center with just six students.', 0),
            ('1968', 'The school moved to 2838 Selwyn Avenue. By 1971, John Whitaker had become the sole owner.', 1),
            ('2006', "Dr. Michael Lehtinen — who joined as a piano instructor in 1995 — became Director upon Mr. Whitaker's retirement. The school also moved to a newly constructed, custom-designed home at Seneca Commons near Park Road.", 2),
            ('Today', "Our facility includes eight teaching studios and a beautiful recital hall designed with aural and visual needs in mind. From our first six students to today's thriving community, our mission is unchanged: music education for all.", 3),
        ]:
            HomeHistoryItem.objects.create(year=year, description=desc, sort_order=order)

        self.stdout.write(self.style.SUCCESS('Successfully seeded initial Southern Park site content.'))
