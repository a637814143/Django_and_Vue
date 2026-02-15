from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from campus_store.accounts.permissions import RolePermission

from .models import Comment, Post, Reaction
from .serializers import CommentSerializer, PostSerializer, ReactionSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [RolePermission]
    allowed_roles = ["CONSUMER", "MERCHANT", "ADMIN"]

    def get_queryset(self):
        user = self.request.user
        qs = Post.objects.prefetch_related("comments", "reactions", "media_files")
        if user.role == user.Role.ADMIN:
            return qs
        if user.role == user.Role.MERCHANT:
            return qs.exclude(visibility=Post.Visibility.INTERNAL)
        return qs.filter(visibility=Post.Visibility.PUBLIC)

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            message=serializer.validated_data["message"],
        )
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def react(self, request, pk=None):
        post = self.get_object()
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reaction, _ = Reaction.objects.update_or_create(
            post=post,
            author=request.user,
            defaults={"reaction_type": serializer.validated_data["reaction_type"]},
        )
        return Response(ReactionSerializer(reaction).data)
