from django.contrib import admin
from .models import RecitalProgram


@admin.register(RecitalProgram)
class RecitalProgramAdmin(admin.ModelAdmin):
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
