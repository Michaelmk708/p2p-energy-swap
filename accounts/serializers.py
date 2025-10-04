# users/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "name")
        read_only_fields = ("id", "email", "username", "name")

    def get_name(self, obj):
        # Prefer first_name + last_name when available, otherwise username or email prefix
        full = " ".join(filter(None, [obj.first_name, obj.last_name])).strip()
        if full:
            return full
        if getattr(obj, "username", None):
            return obj.username
        return (obj.email or "").split("@")[0]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "password", "first_name", "last_name")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        # Pop username if not provided; some User models require it
        username = validated_data.get("username") or validated_data.get("email")
        if "username" not in validated_data:
            validated_data["username"] = username
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user