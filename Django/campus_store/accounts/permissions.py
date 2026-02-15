from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class AuthenticatedOrRedirect(permissions.BasePermission):
    """
    默认权限：要求登录，否则交给异常处理器返回 302。
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class RolePermission(permissions.BasePermission):
    """
    根据视图上定义的 `allowed_roles` 进行角色校验。
    """

    def has_permission(self, request, view):
        roles = getattr(view, "allowed_roles", None)
        if not roles:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == User.Role.ADMIN:
            return True
        return request.user.role in roles
