from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0004_youtube_url_to_charfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryphoto',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('image', '800x600', adapt_rotation=False, allow_fullsize=True, free_crop=True, help_text=None, hide_image_field=False, size_warning=False, verbose_name='cropping'),
        ),
    ]
