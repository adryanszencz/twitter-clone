from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from posts.models import Comment, Like, Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import CommentSerializer, PostSerializer


def annotated_posts(user):
    """Posts com o número de curtidas e comentários e se o usuário atual curtiu."""
    return Post.objects.select_related("author").annotate(
        likes_count=Count("likes", distinct=True),
        comments_count=Count("comments", distinct=True),
        liked_by_me=Exists(Like.objects.filter(post=OuterRef("pk"), user=user)),
    ).order_by("-created_at", "-id")  # com annotate o Meta.ordering não é aplicado


class PostViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """Criar, ver e apagar posts (só o autor apaga), curtir e comentar."""

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return annotated_posts(self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data.update({"likes_count": 0, "comments_count": 0, "liked_by_me": False})
        return response

    @action(detail=True, methods=["post", "delete"])
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        if request.method == "POST":
            _, criado = Like.objects.get_or_create(user=request.user, post=post)
            codigo = status.HTTP_201_CREATED if criado else status.HTTP_200_OK
        else:
            Like.objects.filter(user=request.user, post=post).delete()
            codigo = status.HTTP_200_OK
        return Response(
            {"liked": request.method == "POST", "likes_count": post.likes.count()}, status=codigo
        )

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        if request.method == "POST":
            serializer = CommentSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        comentarios = post.comments.select_related("author")
        page = self.paginate_queryset(comentarios)
        serializer = CommentSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class CommentViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Apagar o próprio comentário."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    queryset = Comment.objects.all()


class FeedView(generics.ListAPIView):
    """Timeline: só os posts das pessoas que o usuário segue, do mais novo para o mais antigo."""

    serializer_class = PostSerializer

    def get_queryset(self):
        return annotated_posts(self.request.user).filter(author__followers_set__follower=self.request.user)


class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return annotated_posts(self.request.user).filter(author=user)
