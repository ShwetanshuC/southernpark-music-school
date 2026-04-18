from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0005_galleryphoto_cropping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryphoto',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('image', '800x675', adapt_rotation=False, allow_fullsize=True, free_crop=True, help_text=None, hide_image_field=False, size_warning=False, verbose_name='cropping'),
        ),
    ]
