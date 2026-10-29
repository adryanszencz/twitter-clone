from rest_framework import serializers

from accounts.serializers import UserSerializer
from posts.models import Comment, Post


def _texto_valido(value, mensagem):
    if not value.strip():
        raise serializers.ValidationError(mensagem)
    return value.strip()


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()
    # os contadores e o "curti" vêm anotados na queryset (ver posts.api.annotated_posts)
    likes_count = serializers.IntegerField(read_only=True, default=0)
    comments_count = serializers.IntegerField(read_only=True, default=0)
    liked_by_me = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Post
        fields = ["id", "author", "content", "created_at", "is_mine", "likes_count", "comments_count", "liked_by_me"]
        read_only_fields = ["id", "author", "created_at"]

    def get_is_mine(self, obj):
        request = self.context.get("request")
        return bool(request and obj.author_id == request.user.id)

    def validate_content(self, value):
        return _texto_valido(value, "O post não pode ficar vazio.")


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "post", "content", "created_at"]
        read_only_fields = ["id", "author", "post", "created_at"]

    def validate_content(self, value):
        return _texto_valido(value, "O comentário não pode ficar vazio.")
