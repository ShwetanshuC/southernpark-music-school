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


def program_view(request):
    from .models import RecitalProgram
    program = RecitalProgram.objects.first()
    return render(request, "pages/program.html", {"program": program})


def program_pdf(request):
    """Proxy the program PDF through Django so PDF.js can fetch it cross-origin-free."""
    from .models import RecitalProgram
    from django.http import Http404, StreamingHttpResponse

    program = RecitalProgram.objects.first()
    if not program:
        raise Http404("No program available")

    try:
        pdf_file = program.pdf.open("rb")
        response = StreamingHttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="program.pdf"'
        return response
    except Exception:
        raise Http404("Program file not found")


def admin_image_proxy(request):
    """Server-side proxy for admin image cropper — bypasses S3 CORS for existing images."""
    from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
    import urllib.request

    if not request.user.is_staff:
        return HttpResponseForbidden()

    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("No URL")

    from django.conf import settings
    bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
    cf_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", "")

    allowed = (
        (bucket and (f"{bucket}.s3." in url or f"s3.amazonaws.com/{bucket}" in url))
        or (cf_domain and cf_domain in url)
        or url.startswith(request.build_absolute_uri("/media/"))
        or (url.startswith("/media/") and not url.startswith("//"))
    )
    if not allowed:
        return HttpResponseForbidden("URL not allowed")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Django/admin-proxy"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            ct = resp.headers.get("Content-Type", "image/jpeg")
            return HttpResponse(resp.read(), content_type=ct)
    except Exception:
        return HttpResponseBadRequest("Failed to fetch image")


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
