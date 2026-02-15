import base64
import binascii
import re
import subprocess

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.middleware import csrf
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .authentication import SessionTokenAuthentication
from .models import CommandLog, SessionToken, LoginLog
from .models import Address
from .permissions import RolePermission
from .serializers import (
    AddressSerializer,
    CommandLogSerializer,
    LoginSerializer,
    RegisterSerializer,
    SessionTokenSerializer,
    UserSerializer,
)

User = get_user_model()
DATA_URL_PATTERN = re.compile(r"^data:(?P<mime>[\w/+.-]+);base64,(?P<data>.+)$")
MAX_AVATAR_BYTES = 5 * 1024 * 1024


def decode_data_url(data_url: str) -> tuple[str, bytes]:
    match = DATA_URL_PATTERN.match(data_url or "")
    if not match:
        raise ValueError("invalid data url")
    mime = match.group("mime")
    encoded = match.group("data")
    try:
        content = base64.b64decode(encoded, validate=True)
    except binascii.Error as exc:
        raise ValueError("invalid base64") from exc
    if len(content) > MAX_AVATAR_BYTES:
        raise ValueError("avatar too large")
    return mime, content


def _issue_token_response(user, request, status_code=status.HTTP_200_OK):
    token = SessionToken.issue(user=user, user_agent=request.META.get("HTTP_USER_AGENT", ""))
    LoginLog.objects.create(
        user=user,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        ip_address=request.META.get("REMOTE_ADDR", None),
    )
    serializer = UserSerializer(user)
    payload = {
        "user": serializer.data,
        "token": token.token,
        "expires_at": token.expires_at,
        "session_id": token.pk,
    }
    response = Response(payload, status=status_code)
    cookie_name = getattr(SessionTokenAuthentication, "cookie_name", "X-SESSION-TOKEN")
    response.set_cookie(
        cookie_name,
        token.token,
        expires=token.expires_at,
        samesite="None",
        httponly=True,
        secure=True,
    )
    response["X-CSRFToken"] = csrf.get_token(request)
    return response


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return _issue_token_response(user, request, status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return _issue_token_response(user, request)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated] # Use direct IsAuthenticated
    def get(self, request):
        user = request.user
        active_tokens = SessionToken.objects.filter(user=user, is_active=True, expires_at__gt=timezone.now())
        return Response(
            {
                "user": UserSerializer(user).data,
                "active_sessions": SessionTokenSerializer(active_tokens, many=True).data,
            }
        )

    def put(self, request):
        user = request.user
        avatar_data = request.data.get("avatar_data", None)
        headline = request.data.get("headline", None)
        store_name = request.data.get("store_name", None)
        updated_fields = []
        if avatar_data is not None:
            if avatar_data == "":
                user.avatar_image = None
                user.avatar_mime = ""
            else:
                try:
                    mime, content = decode_data_url(avatar_data)
                except ValueError as exc:
                    message = str(exc)
                    if message == "avatar too large":
                        return Response({"detail": "头像不能超过 5MB"}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({"detail": "头像格式不正确"}, status=status.HTTP_400_BAD_REQUEST)
                user.avatar_image = content
                user.avatar_mime = mime
            updated_fields.extend(["avatar_image", "avatar_mime"])
        if headline is not None:
            user.headline = headline
            updated_fields.append("headline")
        if store_name is not None and user.role == User.Role.MERCHANT:
            user.store_name = store_name
            updated_fields.append("store_name")
        if updated_fields:
            user.save(update_fields=updated_fields)
        return self.get(request)


class RefreshTokenView(APIView):
    def post(self, request):
        user = request.user
        token = SessionToken.issue(user=user, user_agent=request.META.get("HTTP_USER_AGENT", ""))
        payload = SessionTokenSerializer(token).data
        payload["user"] = UserSerializer(user).data
        response = Response(payload, status=status.HTTP_201_CREATED)
        response.set_cookie(
            "X-SESSION-TOKEN",
            token.token,
            expires=token.expires_at,
            httponly=True,
            samesite="None",
            secure=True,
        )
        return response


class LogoutView(APIView):
    def post(self, request):
        token_value = request.META.get("HTTP_X_SESSION_TOKEN") or request.COOKIES.get("X-SESSION-TOKEN")
        if token_value:
            SessionToken.objects.filter(token=token_value).update(is_active=False)
        logout(request)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("X-SESSION-TOKEN")
        return response


class UserDirectoryViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN, User.Role.MERCHANT]

    def get_queryset(self):
        queryset = User.objects.all().order_by("id")
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(username__icontains=search)
        return queryset


class ResetPasswordView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN]

    def post(self, request):
        user_id = request.data.get("user_id")
        password = request.data.get("password")
        if not user_id or not password:
            return Response({"detail": "需要提供用户ID和新密码"}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response({"detail": "密码长度至少 6 位"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(password)
        user.save(update_fields=["password"])
        return Response({"detail": "密码已重置"})


class AdminTerminalView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.ADMIN]

    def get(self, request):
        logs = CommandLog.objects.select_related("user").all()[:20]
        return Response(CommandLogSerializer(logs, many=True).data)

    def post(self, request):
        command = (request.data.get("command") or "").strip()
        if not command:
            return Response({"detail": "请提供要执行的命令"}, status=status.HTTP_400_BAD_REQUEST)
        if len(command) > 500:
            return Response({"detail": "命令过长"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=settings.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=15,
            )
            combined_output = (completed.stdout + completed.stderr).strip()
            exit_code = completed.returncode
        except subprocess.TimeoutExpired:
            combined_output = "命令执行超时（>15s），已终止。"
            exit_code = -1

        log = CommandLog.objects.create(
            user=request.user,
            command=command,
            output=combined_output,
            exit_code=exit_code,
        )
        serializer = CommandLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [RolePermission]
    allowed_roles = [User.Role.CONSUMER, User.Role.MERCHANT]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_permissions(self):
        # use RolePermission but still need authentication
        return super().get_permissions()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
