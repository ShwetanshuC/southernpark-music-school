from django.core.management.base import BaseCommand
from sitecontent.models import SiteSettings, HomeSection, HomeStat, HomeFeature, HomeHistoryItem

class Command(BaseCommand):
    help = "Force-synchronize literal site content for Southern Park Music School"

    def handle(self, *args, **options):
        # 1. SiteSettings
        ss, _ = SiteSettings.objects.get_or_create(id=1)
        ss.hero_headline = "Where the Good<br><em>Become Great</em>"
        ss.hero_subtitle = "Private music lessons for all ages — inspiring students for over 60 years"
        ss.phone_display = "(704) 676-1002"
        ss.phone_tel = "+17046761002"
        ss.email = "info@southernparkmusicschool.com"
        ss.address = "4805 Park Rd STE 230, Charlotte, NC 28209"
        ss.save()

        # 2. About Us (Concatenated two paragraphs)
        about_text = (
            "Welcome to Southern Park Music School, where creativity and excellence meet. Our mission is to inspire students "
            "of all ages and abilities through personalised lessons, dynamic ensemble experiences, and immersive performance opportunities.\n\n"
            "Whether you're discovering music for the first time or preparing for a professional career, our dedicated faculty "
            "are here to guide you every step of the way. We offer instruction across a wide range of instruments and musical styles — "
            "in a supportive, welcoming community."
        )
        HomeSection.objects.update_or_create(section_type='about', defaults={'title': 'About Us', 'description': about_text})

        # 3. Why Us
        why_us_text = "Since 1964, we've helped Charlotte families discover the joy of music with inspiring teachers, a welcoming community, and spaces built for sound."
        HomeSection.objects.update_or_create(section_type='why_us', defaults={'title': 'Why Choose Southern Park?', 'description': why_us_text})
        
        # 4. History Title
        HomeSection.objects.update_or_create(section_type='history', defaults={'title': 'Our History'})

        # 5. Stats (forced sync with data-suffix logic)
        HomeStat.objects.all().delete()
        stats = [
            ('60', 'Years of Excellence', 0), # data-suffix='+' added in template if needed or included in number
            ('8', 'Private Studios', 1),
            ('10', 'Instruments Taught', 2),
            ('Monthly', 'Student Recitals', 3), # text fallback
        ]
        for num, label, order in stats:
            HomeStat.objects.create(number=num, label=label, sort_order=order)

        # 6. Features (Literal from index.html)
        HomeFeature.objects.all().delete()
        features = [
            ('Recitals that Inspire', 'We host student performances about once a month during the school year — recitals are always free for performers and their guests.', 0),
            ('Studios Built for Sound', 'Eight private studios, each with an acoustic piano. Every piano lesson is taught on a **grand piano** for the best feel and tone.', 1),
            ('Exceptional Faculty', 'Experienced performers and educators — many holding advanced music degrees — with a genuine passion for teaching every student.', 2),
            ('Student Success', 'Our students thrive in festivals and competitions, earn awards, and develop a lifelong love of music that extends well beyond lessons.', 3),
        ]
        for title, text, order in features:
            HomeFeature.objects.create(title=title, text=text, sort_order=order)

        # 7. Timeline (Literal from index.html)
        HomeHistoryItem.objects.all().delete()
        history = [
            ('1964', 'Founded by John Whitaker and Harold Nave, Southern Park Music School opened its doors near Park Road Shopping Center with just six students.', 0),
            ('1968', 'The school moved to 2838 Selwyn Avenue. By 1971, John Whitaker had become the sole owner.', 1),
            ('2006', "Dr. Michael Lehtinen — who joined as a piano instructor in 1995 — became Director upon Mr. Whitaker's retirement. The school also moved to a newly constructed, custom-designed home at Seneca Commons near Park Road.", 2),
            ('Today', 'Our facility includes eight teaching studios and a beautiful recital hall designed with aural and visual needs in mind. From our first six students to today\'s thriving community, our mission is unchanged: music education for all.', 3),
        ]
        for year, desc, order in history:
            HomeHistoryItem.objects.create(year=year, description=desc, sort_order=order)

        self.stdout.write(self.style.SUCCESS('Successfully mirrored 100% of the original Southern Park site content.'))
