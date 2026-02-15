from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        headers = {"Location": "/login"}
        return Response({"detail": "登录状态失效，请重新登录"}, status=status.HTTP_302_FOUND, headers=headers)
    response = exception_handler(exc, context)
    return response
