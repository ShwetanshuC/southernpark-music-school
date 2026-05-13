from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve
from django.shortcuts import render

admin.site.site_header = "Southern Park Music School Admin"
admin.site.site_title = "SPMS Admin"
admin.site.index_title = "Site administration"


def activity_log_view(request):
    from django.contrib.admin.models import LogEntry
    entries = (
        LogEntry.objects
        .select_related("user", "content_type")
        .order_by("-action_time")[:400]
    )
    return render(request, "admin/activity_log.html", {
        "entries": entries,
        "title": "Activity Log",
        "has_permission": True,
    })


urlpatterns = [
    path("admin/activity-log/", admin.site.admin_view(activity_log_view), name="activity_log"),
    path("admin/", admin.site.urls),
    path("faculty/", include("faculty.urls")),
    path("gallery/", include("gallery.urls")),
    path("policies/", include("policies.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", include("pages.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
