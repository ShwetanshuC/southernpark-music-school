from django.contrib import admin
from .models import Instrument, FacultyMember


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "sort_order"]
    list_editable = ["sort_order"]


@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "instrument", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["instrument", "is_active"]
    autocomplete_fields = []  # instrument uses default FK widget with "+" add button
