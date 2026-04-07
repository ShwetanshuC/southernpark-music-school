from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
