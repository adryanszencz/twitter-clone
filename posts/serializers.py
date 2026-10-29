from rest_framework import serializers

from accounts.serializers import UserSerializer
from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "content", "created_at", "is_mine"]
        read_only_fields = ["id", "author", "created_at", "is_mine"]

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return bool(request and obj.author_id == request.user.id)

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("O post não pode ficar vazio.")
        return value.strip()
