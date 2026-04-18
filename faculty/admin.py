from django.contrib import admin
from image_cropping import ImageCroppingMixin
from .models import Instrument, FacultyMember


class CroppingAdminMediaMixin:
    class Media:
        js = ("js/admin-image-cropping.js",)


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "sort_order"]
    list_editable = ["sort_order"]


@admin.register(FacultyMember)
class FacultyMemberAdmin(CroppingAdminMediaMixin, ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["name", "title", "instrument", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["instrument", "is_active"]
    autocomplete_fields = []

    fieldsets = (
        ("Photo", {
            "fields": ("photo", "photo_cropping"),
            "description": (
                "<div style='background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:12px 16px;margin-bottom:8px'>"
                "<strong style='font-size:1.05em'>&#128247; How to crop the photo:</strong><br>"
                "<ol style='margin:8px 0 0 16px;padding:0;line-height:1.9'>"
                "<li>Click <strong>Choose File</strong> to upload a photo.</li>"
                "<li>A square crop box will appear on the photo.</li>"
                "<li><strong>Click and drag</strong> the box to center it on the teacher's face.</li>"
                "<li>Click <strong>Save</strong> when done.</li>"
                "</ol></div>"
            ),
        }),
        ("Teacher Information", {
            "fields": ("name", "title", "instrument", "bio"),
        }),
        ("Display Settings", {
            "fields": ("sort_order", "is_active"),
        }),
    )
