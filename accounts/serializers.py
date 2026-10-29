from django.contrib.auth import authenticate, password_validation
from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "name", "display_name", "bio", "avatar"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "email", "name", "password"]
        extra_kwargs = {"email": {"required": False}, "name": {"required": False}}

    def validate(self, attrs):
        user = User(username=attrs.get("username"), email=attrs.get("email", ""))
        password_validation.validate_password(attrs["password"], user)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Usuário ou senha inválidos.")
        attrs["user"] = user
        return attrs
