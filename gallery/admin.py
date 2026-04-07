from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryPhoto, GalleryVideo


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ["thumbnail_preview", "display_name", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_display_links = ["thumbnail_preview", "display_name"]

    @admin.display(description="Preview")
    def thumbnail_preview(self, obj):
        if obj.image:
            try:
                url = obj.image.url
                return format_html(
                    '<img src="{}" style="height:48px;width:64px;object-fit:cover;border-radius:4px;" />',
                    url,
                )
            except Exception:
                pass
        return "—"

    @admin.display(description="Title / Caption")
    def display_name(self, obj):
        if obj.caption:
            return obj.caption
        # Fall back to filename without path
        if obj.image and obj.image.name:
            return obj.image.name.split("/")[-1]
        return f"Photo {obj.pk}"


@admin.register(GalleryVideo)
class GalleryVideoAdmin(admin.ModelAdmin):
    list_display = ["title", "youtube_url", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
