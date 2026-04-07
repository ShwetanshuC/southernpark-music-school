from django.db import migrations
import re


def fix_phone_format(apps, schema_editor):
    """Replace dot-separated phone numbers with dash format.
    e.g. 704.676.1002  → (704) 676-1002
         980.555.0123  → 980-555-0123
    """
    SiteSettings = apps.get_model('sitecontent', 'SiteSettings')
    for ss in SiteSettings.objects.all():
        original = ss.phone_display
        # Normalize dot-separated 10-digit numbers: NXX.NXX.XXXX
        fixed = re.sub(
            r'(\d{3})\.(\d{3})\.(\d{4})',
            r'\1-\2-\3',
            original
        )
        if fixed != original:
            ss.phone_display = fixed
            ss.save()


class Migration(migrations.Migration):
    dependencies = [
        ('sitecontent', '0008_populate_home_data'),
    ]

    operations = [
        migrations.RunPython(fix_phone_format, migrations.RunPython.noop),
    ]
