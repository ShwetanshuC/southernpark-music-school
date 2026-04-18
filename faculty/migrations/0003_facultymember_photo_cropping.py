from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0002_add_instrument_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='facultymember',
            name='photo_cropping',
            field=image_cropping.fields.ImageRatioField('photo', '400x400', adapt_rotation=False, allow_fullsize=True, free_crop=False, help_text=None, hide_image_field=False, size_warning=False, verbose_name='photo cropping'),
        ),
    ]
