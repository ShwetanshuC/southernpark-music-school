from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryPhoto, GalleryVideo


class ImageToolsAdminMixin:
    class Media:
        css = {"all": [
            "https://unpkg.com/cropperjs@1.6.2/dist/cropper.min.css",
            "css/admin-image-cropping.css",
        ]}
        js = [
            "https://unpkg.com/cropperjs@1.6.2/dist/cropper.min.js",
            "js/admin-image-cropping.js",
            "js/admin-focal-point-picker.js",
        ]


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(ImageToolsAdminMixin, admin.ModelAdmin):
    list_display = ["thumbnail_preview", "display_name", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_display_links = ["thumbnail_preview", "display_name"]

    fieldsets = (
        ("Desktop Image", {
            "fields": ("image", "image_focal_y"),
            "description": "Shown on desktop. Displayed at ~260×200 px in the grid.",
        }),
        ("Mobile Image", {
            "fields": ("image_mobile", "image_focal_y_mobile"),
            "description": "Optional: separate image for phones (&lt;640 px). Falls back to the desktop image if empty.",
        }),
        ("Details", {
            "fields": ("caption", "sort_order", "is_active"),
        }),
    )

    @admin.display(description="Preview")
    def thumbnail_preview(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<img src="{}" style="height:48px;width:64px;object-fit:cover;object-position:center {}%;border-radius:4px;" />',
                    obj.image.url, obj.image_focal_y,
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
