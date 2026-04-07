from django.db import models


class Instrument(models.Model):
    """A music instrument / teaching category. Admins can add new ones at any time."""
    name = models.CharField(max_length=100, unique=True)
    # slug used by views.py for grouping logic (e.g. "piano", "violin viola")
    slug = models.CharField(
        max_length=60,
        unique=True,
        help_text="Internal key used for grouping (lowercase, spaces OK). E.g. 'piano', 'violin viola'.",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Instrument"
        verbose_name_plural = "Instruments"

    def __str__(self) -> str:
        return self.name


class FacultyMember(models.Model):
    name = models.CharField(max_length=120)
    title = models.CharField(max_length=120)
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty",
        help_text="Select an instrument category. Use the + button to add a new one.",
    )
    photo = models.ImageField(upload_to="faculty/", blank=True, null=True)
    bio = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Faculty Member"
        verbose_name_plural = "Faculty Members"

    def __str__(self) -> str:
        return self.name

    # Convenience property so templates/views can still do .instrument_tag
    @property
    def instrument_tag(self) -> str:
        return self.instrument.slug if self.instrument else ""
