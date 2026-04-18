from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitecontent', '0010_sitesettings_hero_headline_richtext'),
    ]

    operations = [
        migrations.AddField(
            model_name='homestat',
            name='link_url',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '— No link (stat is just text, not clickable) —'),
                    ('/faculty/', 'Teachers / Faculty page'),
                    ('/gallery/', 'Photo Gallery page'),
                    ('/calendar/', 'Calendar page'),
                    ('/policies/', 'Policies page'),
                ],
                default='',
                help_text=(
                    'Pick a page from the list. When someone clicks this stat on the website, '
                    'they will be taken to that page. Leave blank if you do not want it to be clickable.'
                ),
                max_length=200,
                verbose_name='Links to page',
            ),
        ),
    ]
