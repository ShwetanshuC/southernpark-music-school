import json
from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
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
    list_display = ["sort_order", "name", "slug"]


@admin.register(FacultyMember)
class FacultyMemberAdmin(AutoBackupMixin, ImageToolsAdminMixin, admin.ModelAdmin):
    list_display = ["name", "title", "instrument", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["instrument", "is_active"]
    change_list_template = "admin/faculty/facultymember/change_list.html"

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

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path("reorder/", self.admin_site.admin_view(self.reorder_view), name="faculty_reorder"),
            path("reorder/save/", self.admin_site.admin_view(self.reorder_save), name="faculty_reorder_save"),
        ]
        return custom + urls

    def reorder_view(self, request):
        instruments = list(Instrument.objects.order_by("sort_order", "name"))
        all_members = list(
            FacultyMember.objects.select_related("instrument").order_by("sort_order", "name")
        )
        assigned = set()
        groups = []
        for inst in instruments:
            members = [m for m in all_members if m.instrument_id == inst.pk]
            for m in members:
                assigned.add(m.pk)
            groups.append({"instrument": inst, "members": members})
        leftover = [m for m in all_members if m.pk not in assigned]
        context = {
            **self.admin_site.each_context(request),
            "title": "Faculty Layout",
            "groups": groups,
            "leftover": leftover,
            "opts": self.model._meta,
        }
        return render(request, "admin/faculty/reorder.html", context)

    def reorder_save(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)
        try:
            data = json.loads(request.body)
            instrument_ids = data.get("instruments", [])
            faculty_items = data.get("faculty", [])
            for i, inst_id in enumerate(instrument_ids):
                Instrument.objects.filter(pk=inst_id).update(sort_order=i)
            for item in faculty_items:
                FacultyMember.objects.filter(pk=item["id"]).update(
                    sort_order=item["order"],
                    instrument_id=item["instrument_id"] or None,
                )
            _backup()
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
