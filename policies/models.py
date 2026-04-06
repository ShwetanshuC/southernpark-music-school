from django.db import models
from ckeditor.fields import RichTextField

class PolicySection(models.Model):
    title = models.CharField(max_length=120)
    body = RichTextField()
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Policy Section"
        verbose_name_plural = "Policy Sections"

    def __str__(self) -> str:
        return self.title
