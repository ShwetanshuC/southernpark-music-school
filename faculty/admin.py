from django.contrib import admin
from .models import Instrument, FacultyMember


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


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "sort_order"]
    list_editable = ["sort_order"]


@admin.register(FacultyMember)
class FacultyMemberAdmin(ImageToolsAdminMixin, admin.ModelAdmin):
    list_display = ["name", "title", "instrument", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["instrument", "is_active"]

    fieldsets = (
        ("Desktop Photo", {
            "fields": ("photo", "image_focal_y"),
            "description": "Shown on desktop. The card crops the photo to a square (roughly 240×240 px).",
        }),
        ("Mobile Photo", {
            "fields": ("photo_mobile", "image_focal_y_mobile"),
            "description": "Optional: separate photo for phones (&lt;576 px). Falls back to the desktop photo if empty.",
        }),
        ("Teacher Information", {
            "fields": ("name", "title", "instrument", "bio"),
        }),
        ("Display Settings", {
            "fields": ("sort_order", "is_active"),
        }),
    )
