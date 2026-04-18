from django.contrib import admin
from django.utils.html import format_html
from image_cropping import ImageCroppingMixin
from .models import GalleryPhoto, GalleryVideo


class CroppingAdminMediaMixin:
    class Media:
        js = ("js/admin-image-cropping.js",)


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(CroppingAdminMediaMixin, ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["thumbnail_preview", "display_name", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_display_links = ["thumbnail_preview", "display_name"]

    fieldsets = (
        ("Photo", {
            "fields": ("image", "cropping"),
            "description": (
                "<div style='background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:12px 16px;margin-bottom:8px'>"
                "<strong style='font-size:1.05em'>&#128247; How to use the crop tool:</strong><br>"
                "<ol style='margin:8px 0 0 16px;padding:0;line-height:1.9'>"
                "<li>Click <strong>Choose File</strong> to upload a photo.</li>"
                "<li>A crop box will appear on the image below.</li>"
                "<li><strong>Click and drag</strong> the box to choose which part of the photo to show.</li>"
                "<li>Drag the <strong>corners</strong> to resize the crop area.</li>"
                "<li>Click <strong>Save</strong> when you are happy with the selection.</li>"
                "</ol></div>"
            ),
        }),
        ("Details", {
            "fields": ("caption", "sort_order", "is_active"),
        }),
    )

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
        if obj.image and obj.image.name:
            return obj.image.name.split("/")[-1]
        return f"Photo {obj.pk}"


@admin.register(GalleryVideo)
class GalleryVideoAdmin(admin.ModelAdmin):
    list_display = ["title", "youtube_url", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
