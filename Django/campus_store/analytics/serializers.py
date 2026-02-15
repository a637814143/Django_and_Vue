from rest_framework import serializers

from .models import MetricSnapshot


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = ["id", "key", "value", "captured_at", "metadata"]
