from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, path
from .models import SiteSettings, HeroSlide, HomeSection, HomeStat, HomeFeature, HomeHistoryItem


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

_ALERT_COLOR_HELP = (
    "<div style='margin-top:8px'>"
    "<strong>Recommended alert colors:</strong>"
    "<table style='border-collapse:collapse;margin-top:6px;font-size:0.85em'>"
    "<tr>"
    "<td style='padding:4px 8px;background:#b00216;color:#fff;border-radius:4px 0 0 4px'>&#9632; #b00216</td>"
    "<td style='padding:4px 8px;color:#555'>Critical / Emergency — bright red</td>"
    "</tr>"
    "<tr>"
    "<td style='padding:4px 8px;background:#C2410C;color:#fff;border-radius:4px 0 0 4px'>&#9632; #C2410C</td>"
    "<td style='padding:4px 8px;color:#555'>Warning / Important — brand orange (blends with site palette)</td>"
    "</tr>"
    "<tr>"
    "<td style='padding:4px 8px;background:#92400E;color:#fff;border-radius:4px 0 0 4px'>&#9632; #92400E</td>"
    "<td style='padding:4px 8px;color:#555'>Informational — warm amber-brown</td>"
    "</tr>"
    "<tr>"
    "<td style='padding:4px 8px;background:#1e5c2e;color:#fff;border-radius:4px 0 0 4px'>&#9632; #1e5c2e</td>"
    "<td style='padding:4px 8px;color:#555'>Positive / Good news — deep green</td>"
    "</tr>"
    "<tr>"
    "<td style='padding:4px 8px;background:#1d4ed8;color:#fff;border-radius:4px 0 0 4px'>&#9632; #1d4ed8</td>"
    "<td style='padding:4px 8px;color:#555'>Neutral notice — navy blue</td>"
    "</tr>"
    "</table>"
    "</div>"
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Alert Banner", {
            "fields": ("alert_enabled", "alert_message", "alert_color"),
            "description": _ALERT_COLOR_HELP,
        }),
        ("Contact Information", {
            "fields": ("phone_display", "phone_tel", "email", "address", "hours_weekday", "hours_saturday"),
        }),
        ("Calendar", {
            "fields": ("calendar_embed_url",),
        }),
        ("Home Page Text", {
            "fields": ("hero_headline", "hero_subtitle", "stats_description"),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.objects.first()
        if obj:
            return redirect(reverse('admin:sitecontent_sitesettings_change', args=(obj.id,)))
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('backup-now/', self.admin_site.admin_view(self.backup_now_view), name='sitecontent_backup_now'),
        ]
        return custom + urls

    def backup_now_view(self, request):
        from sitecontent.s3_backup import backup_db
        try:
            backup_db()
            messages.success(request, "Database backed up to S3 successfully.")
        except Exception as e:
            messages.error(request, f"Backup failed: {e}")
        return HttpResponseRedirect(reverse('admin:sitecontent_sitesettings_changelist'))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['backup_url'] = reverse('admin:sitecontent_backup_now')
        return super().change_view(request, object_id, form_url, extra_context)

@admin.register(HeroSlide)
class HeroSlideAdmin(ImageToolsAdminMixin, admin.ModelAdmin):
    list_display = ["__str__", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]

    fieldsets = (
        ('Desktop Image', {
            'fields': ('image', 'image_focal_y'),
            'description': 'Shown on all screens. Use a wide landscape photo (16:9 or wider recommended).',
        }),
        ('Mobile Image', {
            'fields': ('image_mobile', 'image_focal_y_mobile', 'image_focal_x_mobile'),
            'description': 'Optional: a portrait or tighter crop shown on phones (&lt;640 px). Leave empty to use the desktop image on mobile too. Both focal point pickers show accurate mobile crop previews.',
        }),
        ('Details', {
            'fields': ('image_url', 'alt'),
        }),
        ('Display', {
            'fields': ('sort_order', 'is_active'),
        }),
    )

@admin.register(HomeSection)
class HomeSectionAdmin(ImageToolsAdminMixin, admin.ModelAdmin):
    list_display = ["get_section_type_display", "title"]
    readonly_fields = ["section_type"]

    fieldsets = (
        ('Section Setup', {
            'fields': ('section_type',),
        }),
        ('Content', {
            'fields': ('title', 'description'),
        }),
        ('Desktop Image', {
            'fields': ('image', 'image_focal_y'),
            'description': 'Shown on desktop (≥768 px). Image appears at roughly 2:1 aspect ratio.',
        }),
        ('Mobile Image', {
            'fields': ('image_mobile', 'image_focal_y_mobile', 'image_focal_x_mobile'),
            'description': 'Optional: separate image for phones (&lt;768 px). The image fills full width at fixed height — a tighter or portrait crop often works better here. Both focal point pickers show accurate mobile crop previews.',
        }),
    )

@admin.register(HomeStat)
class HomeStatAdmin(admin.ModelAdmin):
    list_display = ["number", "label", "link_url_display", "sort_order"]
    list_editable = ["sort_order"]
    fieldsets = (
        ("Stat Content", {
            "fields": ("number", "label", "sort_order"),
        }),
        ("Link Setting", {
            "fields": ("link_url",),
        }),
    )

    @admin.display(description="Links To")
    def link_url_display(self, obj):
        if obj.link_url:
            return obj.get_link_url_display()
        return "— no link —"

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
