from django.db import models


class MetricSnapshot(models.Model):
    key = models.CharField(max_length=64)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    captured_at = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-captured_at"]

    def __str__(self):
        return f"{self.key} @ {self.captured_at:%Y-%m-%d}"
