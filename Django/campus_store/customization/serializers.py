from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import WishRequest, WishTimelineEntry

User = get_user_model()


class WishTimelineSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WishTimelineEntry
        fields = ["id", "message", "author", "created_at"]


class WishRequestSerializer(serializers.ModelSerializer):
    consumer = serializers.StringRelatedField(read_only=True)
    merchant = serializers.StringRelatedField(read_only=True)
    timeline = WishTimelineSerializer(many=True, read_only=True)

    class Meta:
        model = WishRequest
        fields = [
            "id",
            "title",
            "description",
            "consumer",
            "merchant",
            "status",
            "attachments",
            "budget",
            "due_date",
            "admin_notes",
            "timeline",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["consumer"] = self.context["request"].user
        return super().create(validated_data)
