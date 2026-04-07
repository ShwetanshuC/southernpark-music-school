from django.db import migrations

def populate_home_data(apps, schema_editor):
    SiteSettings = apps.get_model('sitecontent', 'SiteSettings')
    HomeSection = apps.get_model('sitecontent', 'HomeSection')
    HomeStat = apps.get_model('sitecontent', 'HomeStat')
    HomeFeature = apps.get_model('sitecontent', 'HomeFeature')
    HomeHistoryItem = apps.get_model('sitecontent', 'HomeHistoryItem')

    # 1. SiteSettings
    ss, _ = SiteSettings.objects.get_or_create(id=1)
    ss.hero_headline = "Where the Good<br><em>Become Great</em>"
    ss.hero_subtitle = "Private music lessons for all ages — inspiring students for over 60 years"
    ss.phone_display = "(704) 676-1002"
    ss.phone_tel = "+17046761002"
    ss.email = "info@southernparkmusicschool.com"
    ss.address = "4805 Park Rd STE 230\nCharlotte, NC 28209"
    ss.save()

    # 2. Home Sections
    about_text = (
        "Founded by John Whitaker and Harold Nave, Southern Park Music School opened its doors near Park Road Shopping Center in 1964 "
        "with just six students. In 1968, the school moved to 2838 Selwyn Avenue. By 1971, John Whitaker had become the sole owner of the school.\n\n"
        "Dr. Michael Lehtinen joined the faculty as a piano instructor in 1995 and became Director upon Mr. Whitaker's retirement in 2006. "
        "In early 2006, the school moved to a newly constructed, custom-designed facility at Seneca Commons near Park Road.\n\n"
        "Today, Southern Park Music School thrives with eight private teaching studios, each equipped with an acoustic piano, "
        "and a beautiful recital hall designed to showcase our students' talent."
    )
    HomeSection.objects.update_or_create(section_type='about', defaults={
        'title': 'About Southern Park',
        'description': about_text
    })

    why_us_text = (
        "Since 1964, we've helped Charlotte families discover the joy of music with inspiring teachers, "
        "a welcoming community, and spaces built for sound. Every student is unique, and our "
        "private lesson approach allows us to tailor every moment to your goals and pace."
    )
    HomeSection.objects.update_or_create(section_type='why_us', defaults={
        'title': 'Why Choose Southern Park?',
        'description': why_us_text
    })
    
    HomeSection.objects.update_or_create(section_type='history', defaults={
        'title': 'Our History'
    })

    # 3. Stats
    HomeStat.objects.all().delete()
    stats = [
        ('60+', 'Years of Excellence', 0),
        ('8', 'Staff Studios', 1),
        ('11', 'Teachers', 2),
        ('Monthly', 'Recitals', 3),
    ]
    for num, label, order in stats:
        HomeStat.objects.create(number=num, label=label, sort_order=order)

    # 4. Features
    HomeFeature.objects.all().delete()
    features = [
        ('Experience', 'Our dedicated faculty are experienced performers and educators with a passion for teaching.', 0),
        ('Grand Pianos', 'All piano lessons are taught on well-maintained grand pianos for the best sound and touch.', 1),
        ('Performance', 'We provide regular recital opportunities in our custom-designed recital hall to build confidence.', 2),
        ('Success', 'Our students excel in local and regional festivals, competitions, and college auditions.', 3),
    ]
    for title, text, order in features:
        HomeFeature.objects.create(title=title, text=text, sort_order=order)

    # 5. History
    HomeHistoryItem.objects.all().delete()
    history = [
        ('1964', 'Southern Park Music School founded by John Whitaker and Harold Nave.', 0),
        ('1968', 'Moved to Selwyn Avenue location and John Whitaker became sole owner.', 1),
        ('2006', 'Moved to Seneca Commons location; Dr. Michael Lehtinen becomes Director.', 2),
        ('Today', 'A thriving community of musicians and students in Charlotte.', 3),
    ]
    for year, desc, order in history:
        HomeHistoryItem.objects.create(year=year, description=desc, sort_order=order)

class Migration(migrations.Migration):
    dependencies = [
        ('sitecontent', '0007_alter_heroslide_cropping_alter_homesection_cropping'),
    ]

    operations = [
        migrations.RunPython(populate_home_data),
    ]
