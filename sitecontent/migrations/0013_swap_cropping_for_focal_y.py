from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitecontent', '0012_homesection_cropping_about'),
    ]

    operations = [
        # HeroSlide: remove old Jcrop field, add focal_y
        migrations.RemoveField(model_name='heroslide', name='cropping'),
        migrations.AddField(
            model_name='heroslide',
            name='image_focal_y',
            field=models.PositiveSmallIntegerField(
                default=50,
                help_text='Vertical focal point (0=top, 50=center, 100=bottom). Drag the preview bar above to set this.',
            ),
        ),
        # HomeSection: remove both Jcrop fields, add focal_y
        migrations.RemoveField(model_name='homesection', name='cropping'),
        migrations.RemoveField(model_name='homesection', name='cropping_about'),
        migrations.AddField(
            model_name='homesection',
            name='image_focal_y',
            field=models.PositiveSmallIntegerField(
                default=50,
                help_text='Vertical focal point (0=top, 50=center, 100=bottom). Drag the preview bar above to set this.',
            ),
        ),
    ]
