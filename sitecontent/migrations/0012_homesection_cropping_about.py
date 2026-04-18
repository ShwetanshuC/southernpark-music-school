from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sitecontent', '0011_homestat_link_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='homesection',
            name='cropping_about',
            field=image_cropping.fields.ImageRatioField('image', '1200x585', adapt_rotation=False, allow_fullsize=True, free_crop=False, help_text=None, hide_image_field=False, size_warning=False, verbose_name='cropping about'),
        ),
    ]
