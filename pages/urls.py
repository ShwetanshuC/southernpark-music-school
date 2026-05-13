from django.urls import path
from django.http import HttpResponse
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("healthcheck", lambda r: HttpResponse("OK"), name="healthcheck"),
    path("program/", views.program_view, name="program"),
]
