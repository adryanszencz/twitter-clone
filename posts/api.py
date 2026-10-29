from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from posts.models import Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import PostSerializer


class PostViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """Criar, ver e apagar posts (só o autor apaga)."""

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Post.objects.select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FeedView(generics.ListAPIView):
    """Timeline: só os posts das pessoas que o usuário segue, do mais novo para o mais antigo."""

    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(author__followers_set__follower=self.request.user).select_related("author")


class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Post.objects.filter(author=user).select_related("author")
