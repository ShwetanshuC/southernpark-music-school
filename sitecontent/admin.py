from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import SiteSettings, HeroSlide, HomeSection, HomeStat, HomeFeature, HomeHistoryItem
from image_cropping import ImageCroppingMixin

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

@admin.register(HeroSlide)
class HeroSlideAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["__str__", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]

@admin.register(HomeSection)
class HomeSectionAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["get_section_type_display", "title"]
    readonly_fields = ["section_type"]

@admin.register(HomeStat)
class HomeStatAdmin(admin.ModelAdmin):
    list_display = ["number", "label", "sort_order"]
    list_editable = ["sort_order"]

@admin.register(HomeFeature)
class HomeFeatureAdmin(admin.ModelAdmin):
    list_display = ["title", "sort_order"]
    list_editable = ["sort_order"]

@admin.register(HomeHistoryItem)
class HomeHistoryItemAdmin(admin.ModelAdmin):
    list_display = ["year", "sort_order"]
    list_editable = ["sort_order"]

# Simplified User Management
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

class SimplifiedUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
    )
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ()
    filter_horizontal = ()

    def save_model(self, request, obj, form, change):
        if not obj.is_staff:
            obj.is_staff = True
        super().save_model(request, obj, form, change)

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, SimplifiedUserAdmin)
