from django.utils import timezone
from rest_framework import authentication, exceptions

from .models import SessionToken


class SessionTokenAuthentication(authentication.BaseAuthentication):
    """
    读取自定义会话令牌（Header: X-SESSION-TOKEN 或 Cookie）。
    """

    header_name = "HTTP_X_SESSION_TOKEN"
    cookie_name = "X-SESSION-TOKEN"

    def authenticate(self, request):
        token_value = request.META.get(self.header_name) or request.COOKIES.get(self.cookie_name)
        if not token_value:
            return None
        try:
            session_token = SessionToken.objects.select_related("user").get(
                token=token_value, is_active=True
            )
        except SessionToken.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("无效的令牌", code="invalid_token") from exc

        if session_token.expires_at <= timezone.now():
            session_token.mark_inactive()
            raise exceptions.AuthenticationFailed("令牌已过期", code="expired_token")

        user = session_token.user
        if not user.is_active:
            raise exceptions.AuthenticationFailed("账号已停用", code="inactive_account")

        request.session["last_token_id"] = session_token.pk
        return (user, session_token)
