from django.db import models


class RecitalProgram(models.Model):
    title = models.CharField(max_length=200, default="Recital Program")
    pdf = models.FileField(upload_to="programs/")
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recital Program"
        verbose_name_plural = "Recital Program"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Only one program record at a time — replace it
        self.__class__.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)
