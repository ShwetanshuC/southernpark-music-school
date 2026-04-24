import re
from django.db import models


class GalleryPhoto(models.Model):
    image = models.ImageField(upload_to="gallery/")
    image_focal_y = models.PositiveSmallIntegerField(
        default=50,
        help_text="Vertical focal point (0=top, 50=center, 100=bottom). Drag the preview bar above to set this.",
    )
    image_mobile = models.ImageField(
        upload_to="gallery_mobile/", blank=True, null=True,
        help_text="Optional image for mobile (<640 px). Falls back to the desktop image if empty.",
    )
    image_focal_y_mobile = models.PositiveSmallIntegerField(
        default=50,
        help_text="Vertical focal point on phones (0=top, 50=center, 100=bottom).",
    )
    image_focal_x_mobile = models.PositiveSmallIntegerField(
        default=50,
        help_text="Horizontal focal point on phones (0=left, 50=center, 100=right).",
    )
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Gallery Photo"
        verbose_name_plural = "Gallery Photos"

    def __str__(self) -> str:
        return self.caption or f"Photo {self.id}"


class GalleryVideo(models.Model):
    title = models.CharField(max_length=200)
    youtube_url = models.CharField(
        max_length=500,
        help_text="Paste the YouTube video link, e.g. https://youtu.be/abc123 or https://www.youtube.com/watch?v=abc123",
    )
    caption = models.CharField(max_length=300, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Gallery Video"
        verbose_name_plural = "Gallery Videos"

    def __str__(self) -> str:
        return self.title

    @property
    def embed_src(self) -> str:
        """Convert any YouTube URL format to an embed src URL."""
        raw = (self.youtube_url or "").strip()
        if "youtube.com/embed/" in raw:
            return raw
        # youtu.be/VIDEO_ID
        m = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", raw)
        if m:
            return f"https://www.youtube.com/embed/{m.group(1)}"
        # youtube.com/watch?v=VIDEO_ID or youtube.com/shorts/VIDEO_ID
        m = re.search(r"(?:[?&]v=|/shorts/)([A-Za-z0-9_-]{11})", raw)
        if m:
            return f"https://www.youtube.com/embed/{m.group(1)}"
        return raw
