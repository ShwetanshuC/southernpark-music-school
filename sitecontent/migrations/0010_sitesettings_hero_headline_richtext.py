import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):
    """Change hero_headline from CharField to RichTextField so admin shows WYSIWYG editor."""

    dependencies = [
        ('sitecontent', '0009_fix_phone_format'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='hero_headline',
            field=ckeditor.fields.RichTextField(
                config_name='minimal',
                default='Where the Good<br><em>Become Great</em>',
            ),
        ),
    ]
