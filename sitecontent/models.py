from __future__ import annotations
from django.db import models


class SiteSettings(models.Model):
    alert_enabled = models.BooleanField(default=True)
    alert_message = models.CharField(
        max_length=255,
        default="In the event of adverse weather, please contact your teacher individually to arrange a virtual lesson.",
    )
    alert_color = models.CharField(
        max_length=7,
        default="#b00216",
        help_text="Hex color code for the alert banner background (e.g. #b00216)"
    )
    phone_display = models.CharField(max_length=60, default="(704) 676-1002")
    phone_tel = models.CharField(max_length=30, default="+17046761002")
    email = models.EmailField(default="info@southernparkmusicschool.com")
    address = models.TextField(default="4805 Park Rd STE 230\nCharlotte, NC 28209")
    hours_weekday = models.CharField(max_length=30, default="9AM\u20139PM")
    hours_saturday = models.CharField(max_length=30, default="9AM\u20132PM")
    calendar_embed_url = models.URLField(max_length=1000, blank=True, default="")

    class Meta:
        verbose_name = "Global Configuration"
        verbose_name_plural = "Global Configuration"

    def __str__(self) -> str:
        return "Global Configuration"


from image_cropping import ImageRatioField

class HeroSlide(models.Model):
    image = models.ImageField(upload_to="hero/", blank=True, null=True)
    cropping = ImageRatioField("image", "1600x900")
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
