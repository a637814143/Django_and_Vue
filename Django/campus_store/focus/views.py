from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from campus_store.accounts.permissions import RolePermission

from .models import FocusVideo, FocusVideoComment, FocusVideoLike
from .serializers import FocusVideoCommentSerializer, FocusVideoSerializer

User = get_user_model()


class FocusVideoViewSet(viewsets.ModelViewSet):
    serializer_class = FocusVideoSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN, User.Role.MERCHANT, User.Role.CONSUMER]

    def get_queryset(self):
        queryset = FocusVideo.objects.select_related("creator").prefetch_related("likes", "comments")
        user = self.request.user
        if not user.is_authenticated or user.role != User.Role.ADMIN:
            queryset = queryset.filter(status=FocusVideo.Status.ACTIVE)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def destroy(self, request, *args, **kwargs):
        video = self.get_object()
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"detail": "请先登录"}, status=status.HTTP_401_UNAUTHORIZED)
        if user != video.creator and user.role != User.Role.ADMIN:
            return Response({"detail": "只能删除自己上传的视频"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        video = self.get_object()
        user = request.user
        like, created = FocusVideoLike.objects.get_or_create(user=user, video=video)
        if not created:
            like.delete()
            video.like_count = max(0, video.like_count - 1)
            liked = False
        else:
            video.like_count = FocusVideoLike.objects.filter(video=video).count()
            liked = True
        video.save(update_fields=["like_count"])
        return Response({"liked": liked, "like_count": video.like_count})

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        video = self.get_object()
        if request.method == "GET":
            qs = video.comments.select_related("author")
            serializer = FocusVideoCommentSerializer(qs, many=True)
            return Response(serializer.data)
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"detail": "评论内容不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        comment = FocusVideoComment.objects.create(video=video, author=request.user, content=content)
        video.comment_count = FocusVideoComment.objects.filter(video=video).count()
        video.save(update_fields=["comment_count"])
        return Response(FocusVideoCommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[RolePermission])
    def deactivate(self, request, pk=None):
        video = self.get_object()
        if request.user.role != User.Role.ADMIN:
            return Response({"detail": "仅管理员可操作"}, status=status.HTTP_403_FORBIDDEN)
        video.status = FocusVideo.Status.DISABLED
        video.save(update_fields=["status"])
        return Response({"status": video.status})

    @action(detail=True, methods=["post"], permission_classes=[RolePermission])
    def restore(self, request, pk=None):
        video = self.get_object()
        if request.user.role != User.Role.ADMIN:
            return Response({"detail": "仅管理员可操作"}, status=status.HTTP_403_FORBIDDEN)
        video.status = FocusVideo.Status.ACTIVE
        video.save(update_fields=["status"])
        return Response({"status": video.status})
