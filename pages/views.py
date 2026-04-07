from django.shortcuts import render
from sitecontent.models import SiteSettings, HeroSlide, HomeSection, HomeStat, HomeFeature, HomeHistoryItem


def home(request):
    site_settings = SiteSettings.objects.first()
    hero_slides = HeroSlide.objects.filter(is_active=True)
    
    # Sections
    about = HomeSection.objects.filter(section_type='about').first()
    why_us = HomeSection.objects.filter(section_type='why_us').first()
    history = HomeSection.objects.filter(section_type='history').first()
    
    # Lists
    stats = HomeStat.objects.all()
    features = HomeFeature.objects.all()
    history_items = HomeHistoryItem.objects.all()
    
    from types import SimpleNamespace
    
    # Enhanced Fallbacks for Content
    if not site_settings:
        site_settings = SimpleNamespace(
            hero_headline="Where the Good<br><em>Become Great</em>",
            hero_subtitle="Private music lessons for all ages — inspiring students for over 60 years",
            email="info@southernparkmusicschool.com"
        )
    
    if not about:
        about = SimpleNamespace(
            title="About Us",
            description="Welcome to Southern Park Music School, where creativity and excellence meet. Our mission is to inspire students of all ages and abilities through personalised lessons, dynamic ensemble experiences, and immersive performance opportunities."
        )
    
    if not why_us:
        why_us = SimpleNamespace(
            title="Why Choose Southern Park?",
            description="Since 1964, we've helped Charlotte families discover the joy of music with inspiring teachers, a welcoming community, and spaces built for sound."
        )

    context = {
        "site_settings": site_settings,
        "hero_slides": hero_slides,
        "about": about,
        "why_us": why_us,
        "history": history,
        "stats": stats,
        "features": features,
        "history_items": history_items,
    }
    return render(request, "pages/home.html", context)


def calendar_view(request):
    return render(request, "pages/calendar.html")


def robots_txt(request):
    from django.http import HttpResponse
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /media/\n"
        "\n"
        "Sitemap: https://southernparkmusicschool.com/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    from django.http import HttpResponse
    from django.utils import timezone
    today = timezone.now().date().isoformat()
    base = "https://southernparkmusicschool.com"
    urls = [
        (f"{base}/",          "weekly",  "1.0"),
        (f"{base}/faculty/",  "monthly", "0.8"),
        (f"{base}/gallery/",  "monthly", "0.6"),
        (f"{base}/calendar/", "weekly",  "0.7"),
        (f"{base}/policies/", "yearly",  "0.5"),
    ]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, freq, priority in urls:
        lines += [
            "  <url>",
            f"    <loc>{loc}</loc>",
            f"    <lastmod>{today}</lastmod>",
            f"    <changefreq>{freq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")
    return HttpResponse("\n".join(lines), content_type="application/xml")
