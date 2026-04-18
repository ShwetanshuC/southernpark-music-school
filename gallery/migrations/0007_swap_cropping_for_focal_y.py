from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0006_alter_galleryphoto_cropping'),
    ]

    operations = [
        migrations.RemoveField(model_name='galleryphoto', name='cropping'),
        migrations.AddField(
            model_name='galleryphoto',
            name='image_focal_y',
            field=models.PositiveSmallIntegerField(
                default=50,
                help_text='Vertical focal point (0=top, 50=center, 100=bottom). Drag the preview bar above to set this.',
            ),
        ),
    ]
