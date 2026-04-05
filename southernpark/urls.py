from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve

admin.site.site_header = "Southern Park Music School Admin"
admin.site.site_title = "SPMS Admin"
admin.site.index_title = "Site administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("faculty/", include("faculty.urls")),
    path("gallery/", include("gallery.urls")),
    path("policies/", include("policies.urls")),
    path("", include("pages.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
