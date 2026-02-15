from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import FocusVideo, FocusVideoComment

User = get_user_model()


class FocusVideoCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FocusVideoComment
        fields = ["id", "author", "content", "created_at"]


class FocusVideoSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    video_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    video_file = serializers.FileField(write_only=True, source="video")
    cover_file = serializers.ImageField(write_only=True, source="cover_image", required=False, allow_null=True)
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = FocusVideo
        fields = [
            "id",
            "title",
            "description",
            "creator",
            "video_url",
            "cover_url",
            "status",
            "like_count",
            "comment_count",
            "is_liked",
            "comments",
            "created_at",
            "video_file",
            "cover_file",
            "can_delete",
        ]
        read_only_fields = [
            "creator",
            "video_url",
            "cover_url",
            "status",
            "like_count",
            "comment_count",
            "is_liked",
            "comments",
            "created_at",
            "can_delete",
        ]

    def get_video_url(self, obj):
        request = self.context.get("request")
        if obj.video and request:
            return request.build_absolute_uri(obj.video.url)
        if obj.video:
            return obj.video.url
        return ""

    def get_cover_url(self, obj):
        request = self.context.get("request")
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        if obj.cover_image:
            return obj.cover_image.url
        return ""

    def get_is_liked(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return obj.likes.filter(user=user).exists()

    def get_comments(self, obj):
        request = self.context.get("request")
        if request and request.query_params.get("with_comments") == "0":
            return []
        comments = obj.comments.all()[:5]
        return FocusVideoCommentSerializer(comments, many=True).data

    def get_can_delete(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if user.role == User.Role.ADMIN:
            return True
        return obj.creator_id == user.id
