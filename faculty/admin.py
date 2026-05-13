from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Instrument, FacultyMember


def _backup():
    try:
        from sitecontent.s3_backup import backup_db
        backup_db()
    except Exception:
        pass


class AutoBackupMixin:
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        _backup()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        _backup()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        _backup()


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
class InstrumentAdmin(AutoBackupMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "slug"]


@admin.register(FacultyMember)
class FacultyMemberAdmin(AutoBackupMixin, ImageToolsAdminMixin, admin.ModelAdmin):
    list_display = ["name", "title", "instrument", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["instrument", "is_active"]

    fieldsets = (
        ("Desktop Photo", {
            "fields": ("photo", "image_focal_y"),
            "description": "Shown on desktop. The card crops the photo to a square (roughly 240×240 px).",
        }),
        ("Mobile Photo", {
            "fields": ("photo_mobile", "image_focal_y_mobile", "image_focal_x_mobile"),
            "description": "Optional: separate photo for phones (&lt;576 px). Falls back to the desktop photo if empty. Both focal point pickers show accurate mobile crop previews.",
        }),
        ("Teacher Information", {
            "fields": ("name", "title", "instrument", "bio"),
        }),
        ("Display Settings", {
            "fields": ("sort_order", "is_active"),
        }),
    )
