import re
from django.db import models
from image_cropping import ImageRatioField


class GalleryPhoto(models.Model):
    image = models.ImageField(upload_to="gallery/")
    # Gallery thumbnails display at ~237×200px (1.18:1); free_crop lets admins adjust freely
    cropping = ImageRatioField("image", "800x675", free_crop=True, allow_fullsize=True)
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
