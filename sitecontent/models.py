from __future__ import annotations
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class SiteSettings(models.Model):
    alert_enabled = models.BooleanField(default=True)
    alert_message = models.CharField(
        max_length=255,
        default="In the event of adverse weather, please contact your teacher individually to arrange a virtual lesson.",
    )
    from colorfield.fields import ColorField
    alert_color = ColorField(default='#b00216', help_text="Color for the alert banner background")
    phone_display = models.CharField(max_length=60, default="(704) 676-1002")
    phone_tel = models.CharField(max_length=30, default="+17046761002")
    email = models.EmailField(default="info@southernparkmusicschool.com")
    address = models.TextField(default="4805 Park Rd STE 230\nCharlotte, NC 28209")
    hours_weekday = models.CharField(max_length=30, default="9AM\u20139PM")
    hours_saturday = models.CharField(max_length=30, default="9AM\u20132PM")
    calendar_embed_url = models.URLField(max_length=1000, blank=True, default="")

    # Home Page Global Text
    hero_headline = CKEditor5Field(config_name='minimal', default="Where the Good<br><em>Become Great</em>")
    hero_subtitle = models.CharField(max_length=255, default="Private music lessons for all ages — inspiring students for over 60 years")
    stats_description = models.TextField(blank=True, default="Since 1964, we've helped Charlotte families discover the joy of music.")

    class Meta:
        verbose_name = "Global Configuration"
        verbose_name_plural = "Global Configuration"

    def __str__(self) -> str:
        return "Global Configuration"


class HeroSlide(models.Model):
    image = models.ImageField(upload_to="hero/", blank=True, null=True)
    image_focal_y = models.PositiveSmallIntegerField(
        default=50,
        help_text="Vertical focal point (0=top, 50=center, 100=bottom). Drag the preview bar above to set this.",
    )
    image_url = models.URLField(blank=True, default="", max_length=800)
    alt = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"

    def __str__(self) -> str:
        return f"Hero Slide {self.sort_order} – {self.alt or 'untitled'}"

class HomeSection(models.Model):
    SECTION_CHOICES = [
        ('about', 'About Us'),
        ('why_us', 'Why Choose Us'),
        ('history', 'Our History'),
    ]
    section_type = models.CharField(max_length=20, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="home/", blank=True, null=True)
    image_focal_y = models.PositiveSmallIntegerField(
        default=50,
        help_text="Vertical focal point (0=top, 50=center, 100=bottom). Drag the preview bar above to set this.",
    )
    
    class Meta:
        verbose_name = "Home Section"
        verbose_name_plural = "Home Sections"

    def __str__(self) -> str:
        return self.get_section_type_display()

class HomeStat(models.Model):
    LINK_CHOICES = [
        ('', '— No link (stat is just text, not clickable) —'),
        ('/faculty/', 'Teachers / Faculty page'),
        ('/gallery/', 'Photo Gallery page'),
        ('/calendar/', 'Calendar page'),
        ('/policies/', 'Policies page'),
    ]
    number = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    link_url = models.CharField(
        max_length=200,
        blank=True,
        default='',
        choices=LINK_CHOICES,
        verbose_name="Links to page",
        help_text=(
            "Pick a page from the list. When someone clicks this stat on the website, "
            "they will be taken to that page. Leave blank if you do not want it to be clickable."
        ),
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
        verbose_name = "Home Stat"
        verbose_name_plural = "Home Stats"

    def __str__(self) -> str:
        return f"{self.number} {self.label}"

class HomeFeature(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
        verbose_name = "Home Feature (Why Choose Us)"
        verbose_name_plural = "Home Features (Why Choose Us)"

    def __str__(self) -> str:
        return self.title

class HomeHistoryItem(models.Model):
    year = models.CharField(max_length=20)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
        verbose_name = "History Timeline Item"
        verbose_name_plural = "History Timeline Items"

    def __str__(self) -> str:
        return f"{self.year}: {self.description[:30]}..."
