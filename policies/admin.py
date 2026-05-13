from django.contrib import admin
from .models import PolicySection


def _backup():
    try:
        from sitecontent.s3_backup import backup_db
        backup_db()
    except Exception:
        pass


@admin.register(PolicySection)
class PolicySectionAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        _backup()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        _backup()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        _backup()
    list_display = ["title", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
