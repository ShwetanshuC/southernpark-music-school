from django.contrib import admin
from .models import RecitalProgram


def _backup():
    try:
        from sitecontent.s3_backup import backup_db
        backup_db()
    except Exception:
        pass


@admin.register(RecitalProgram)
class RecitalProgramAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        _backup()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        _backup()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        _backup()
    fields = ("title", "pdf", "uploaded_at")
    readonly_fields = ("uploaded_at",)

    def has_add_permission(self, request):
        # Allow adding only when no record exists; otherwise force change
        return not RecitalProgram.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return True

    def changelist_view(self, request, extra_context=None):
        # Redirect straight to the single record's change page if one exists
        from django.shortcuts import redirect
        from django.urls import reverse
        qs = RecitalProgram.objects.all()
        if qs.count() == 1:
            return redirect(
                reverse("admin:pages_recitalprogram_change", args=[qs.first().pk])
            )
        return super().changelist_view(request, extra_context)
