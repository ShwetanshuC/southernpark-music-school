from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, path
from .models import SiteSettings, HeroSlide, HomeSection, HomeStat, HomeFeature, HomeHistoryItem
from image_cropping import ImageCroppingMixin

class CroppingAdminMediaMixin:
    class Media:
        js = ("js/admin-image-cropping.js",)

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
class HeroSlideAdmin(CroppingAdminMediaMixin, ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["__str__", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    
    fieldsets = (
        ('Image', {
            'fields': ('image', 'cropping'),
            'description': 'Upload an image and adjust the crop area below. Click and drag to define the 1600x900 crop region. Live preview updates as you crop.',
        }),
        ('Details', {
            'fields': ('image_url', 'alt'),
            'description': 'Alternative image URL (if not uploading) and alt text for accessibility.',
        }),
        ('Display', {
            'fields': ('sort_order', 'is_active'),
        }),
    )

_CROP_HELP_ABOUT = (
    "<div style='background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:12px 16px;margin-bottom:8px'>"
    "<strong style='font-size:1.05em'>&#128247; How to crop this image (About section — wide 2:1 view):</strong><br>"
    "<ol style='margin:8px 0 0 16px;padding:0;line-height:1.9'>"
    "<li>Click <strong>Choose File</strong> to upload a photo.</li>"
    "<li>A wide crop box (matching exactly how this image appears on the site) will appear.</li>"
    "<li><strong>Click and drag</strong> the box to frame the best part of the photo.</li>"
    "<li>Click <strong>Save</strong> when done.</li>"
    "</ol></div>"
)

_CROP_HELP_HISTORY = (
    "<div style='background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:12px 16px;margin-bottom:8px'>"
    "<strong style='font-size:1.05em'>&#128247; How to crop this image (History section — 3:2 view):</strong><br>"
    "<ol style='margin:8px 0 0 16px;padding:0;line-height:1.9'>"
    "<li>Click <strong>Choose File</strong> to upload a photo.</li>"
    "<li>A crop box (matching exactly how this image appears on the site) will appear.</li>"
    "<li><strong>Click and drag</strong> the box to frame the best part of the photo.</li>"
    "<li>Click <strong>Save</strong> when done.</li>"
    "</ol></div>"
)

@admin.register(HomeSection)
class HomeSectionAdmin(CroppingAdminMediaMixin, ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["get_section_type_display", "title"]
    readonly_fields = ["section_type"]

    def get_fieldsets(self, request, obj=None):
        is_about = obj and obj.section_type == 'about'
        crop_field = 'cropping_about' if is_about else 'cropping'
        crop_help = _CROP_HELP_ABOUT if is_about else _CROP_HELP_HISTORY
        return (
            ('Section Setup', {
                'fields': ('section_type',),
            }),
            ('Content', {
                'fields': ('title', 'description'),
            }),
            ('Image', {
                'fields': ('image', crop_field),
                'description': crop_help,
            }),
        )

_STAT_LINK_HELP = (
    "<div style='background:#e8f4fd;border:1px solid #90caf9;border-radius:6px;padding:12px 16px;margin-bottom:8px'>"
    "<strong style='font-size:1.05em'>&#128279; How to make a stat clickable:</strong><br>"
    "<p style='margin:8px 0 0;line-height:1.8'>"
    "Each stat on the home page can link to another page on the website when clicked.<br>"
    "In the <strong>\"Links to page\"</strong> dropdown below, select which page this stat should go to.<br>"
    "If you do not want it to be a link, leave it set to <strong>\"No link\"</strong>."
    "</p></div>"
)

@admin.register(HomeStat)
class HomeStatAdmin(admin.ModelAdmin):
    list_display = ["number", "label", "link_url_display", "sort_order"]
    list_editable = ["sort_order"]
    fieldsets = (
        ("Stat Content", {
            "fields": ("number", "label", "sort_order"),
            "description": "The large number and the label shown beneath it on the home page.",
        }),
        ("Link Setting", {
            "fields": ("link_url",),
            "description": _STAT_LINK_HELP,
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
