# Generated migration — extended with data migration to preserve instrument_tag data.

from django.db import migrations, models
import django.db.models.deletion

INSTRUMENT_SEEDS = [
    ("Piano",                "piano",               0),
    ("Piano & Voice",        "piano voice",         1),
    ("Violin & Viola",       "violin viola",        2),
    ("Violin",               "violin",              3),
    ("Viola",                "viola",               4),
    ("Cello",                "cello",               5),
    ("Flute",                "flute",               6),
    ("Oboe & Flute",         "oboe flute",          7),
    ("Oboe",                 "oboe",                8),
    ("Saxophone & Clarinet", "saxophone clarinet",  9),
    ("Saxophone",            "saxophone",           10),
    ("Clarinet",             "clarinet",            11),
    ("Voice",                "voice",               12),
    ("Guitar",               "guitar",              13),
    ("Drums / Percussion",   "drums",               14),
    ("Staff / Administrator","administrator",       15),
]


def seed_instruments_and_assign(apps, schema_editor):
    Instrument = apps.get_model("faculty", "Instrument")
    FacultyMember = apps.get_model("faculty", "FacultyMember")

    # Create all default instruments
    slug_to_obj = {}
    for name, slug, order in INSTRUMENT_SEEDS:
        obj, _ = Instrument.objects.get_or_create(slug=slug, defaults={"name": name, "sort_order": order})
        slug_to_obj[slug] = obj

    # Assign instrument FK from old instrument_tag value
    for member in FacultyMember.objects.all():
        tag = (member.instrument_tag or "").strip().lower()
        if tag in slug_to_obj:
            member.instrument = slug_to_obj[tag]
            member.save(update_fields=["instrument"])


def reverse_migration(apps, schema_editor):
    # Restore instrument_tag from instrument.slug (best-effort)
    FacultyMember = apps.get_model("faculty", "FacultyMember")
    for member in FacultyMember.objects.all():
        if member.instrument:
            member.instrument_tag = member.instrument.slug
            member.save(update_fields=["instrument_tag"])


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0001_initial'),
    ]

    operations = [
        # 1. Create Instrument model
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.CharField(
                    help_text="Internal key used for grouping (lowercase, spaces OK). E.g. 'piano', 'violin viola'.",
                    max_length=60, unique=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Instrument',
                'verbose_name_plural': 'Instruments',
                'ordering': ['sort_order', 'name'],
            },
        ),
        # 2. Add instrument FK (nullable so existing rows are unaffected initially)
        migrations.AddField(
            model_name='facultymember',
            name='instrument',
            field=models.ForeignKey(
                blank=True,
                help_text='Select an instrument category. Use the + button to add a new one.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='faculty',
                to='faculty.instrument',
            ),
        ),
        # 3. Seed instruments and map existing faculty rows
        migrations.RunPython(seed_instruments_and_assign, reverse_code=reverse_migration),
        # 4. Remove old instrument_tag field
        migrations.RemoveField(
            model_name='facultymember',
            name='instrument_tag',
        ),
    ]
