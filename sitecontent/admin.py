from django.contrib import admin
from django.forms.widgets import TextInput
from .models import SiteSettings, HeroSlide

class ColorPickerWidget(TextInput):
    input_type = "color"

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "alert_color":
            kwargs["widget"] = ColorPickerWidget()
        return super().formfield_for_dbfield(db_field, **kwargs)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


from image_cropping import ImageCroppingMixin

@admin.register(HeroSlide)
class HeroSlideAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["__str__", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

# Remove Group from admin entirely
admin.site.unregister(Group)

class SimplifiedUserAdmin(UserAdmin):
    # Only show these fields
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
    )
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ()
    filter_horizontal = ()

    def save_model(self, request, obj, form, change):
        # Auto-grant staff status so they can log into this admin panel
        if not obj.is_staff:
            obj.is_staff = True
        super().save_model(request, obj, form, change)

admin.site.unregister(User)
admin.site.register(User, SimplifiedUserAdmin)

