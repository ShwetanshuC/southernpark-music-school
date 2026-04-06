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
