import base64

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import CommandLog, SessionToken
from .models import Address

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "headline",
            "store_name",
            "avatar_url",
            "avatar",
        ]

    def get_avatar(self, obj):
        if not obj.avatar_image:
            return None
        encoded = base64.b64encode(obj.avatar_image).decode("ascii")
        mime = obj.avatar_mime or "image/png"
        return f"data:{mime};base64,{encoded}"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    desired_role = serializers.ChoiceField(
        choices=User.Role.choices, required=False, write_only=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "desired_role"]
        extra_kwargs = {
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "email": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        desired_role = validated_data.pop("desired_role", User.Role.CONSUMER)
        if desired_role == User.Role.ADMIN:
            desired_role = User.Role.CONSUMER
        user = User.objects.create_user(**validated_data)
        if desired_role in (User.Role.CONSUMER, User.Role.MERCHANT):
            user.role = desired_role
        user.save(update_fields=["role"])
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError("用户名或密码错误")
        if not user.is_active:
            raise serializers.ValidationError("账号已被停用，请联系管理员")
        attrs["user"] = user
        return attrs


class SessionTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionToken
        fields = ["token", "created_at", "expires_at", "user_agent", "is_active"]


class CommandLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CommandLog
        fields = ["id", "user", "command", "output", "exit_code", "created_at"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "receiver_name",
            "phone",
            "dorm_building",
            "dorm_room",
            "detail",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        # ensure phone trimmed
        phone = attrs.get("phone")
        if phone is not None:
            attrs["phone"] = str(phone).strip()
        return attrs

    def _clear_default(self, user):
        Address.objects.filter(user=user, is_default=True).update(is_default=False)

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        if validated_data.get("is_default"):
            self._clear_default(user)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_default"):
            self._clear_default(instance.user)
        return super().update(instance, validated_data)
