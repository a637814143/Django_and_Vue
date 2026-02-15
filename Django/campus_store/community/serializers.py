from rest_framework import serializers

from .models import Comment, Post, Reaction, PostMedia


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "message", "created_at"]


class ReactionSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reaction
        fields = ["id", "author", "reaction_type", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    media_files = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "cover_image",
            "visibility",
            "author",
            "comments",
            "reactions",
            "media_files",
            "created_at",
            "updated_at",
        ]

    def get_media_files(self, obj):
        files = getattr(obj, "media_files", None)
        qs = files.all() if hasattr(files, "all") else (files or [])
        return [
            {
                "id": media.id,
                "url": media.file.url if hasattr(media.file, "url") else "",
                "media_type": media.media_type,
                "name": media.file.name.split("/")[-1],
            }
            for media in qs
        ]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        media_list = self.context["request"].FILES.getlist("media_files")
        post = super().create(validated_data)
        for uploaded in media_list:
            media_type = "VIDEO" if (uploaded.content_type or "").startswith("video") else "IMAGE"
            PostMedia.objects.create(post=post, file=uploaded, media_type=media_type)
        return post
