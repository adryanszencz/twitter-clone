from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Follow, User
from accounts.serializers import PublicProfileSerializer


class UserSearchView(generics.ListAPIView):
    """Lista/busca usuários (?search=) para encontrar quem seguir."""

    serializer_class = PublicProfileSerializer

    def get_queryset(self):
        queryset = User.objects.exclude(pk=self.request.user.pk).order_by("username")
        termo = self.request.query_params.get("search", "").strip()
        if termo:
            queryset = queryset.filter(Q(username__icontains=termo) | Q(name__icontains=termo))
        return queryset


class PublicProfileView(generics.RetrieveAPIView):
    serializer_class = PublicProfileSerializer
    queryset = User.objects.all()
    lookup_field = "username"


class FollowView(APIView):
    """POST segue, DELETE deixa de seguir o usuário da URL."""

    def post(self, request, username):
        alvo = get_object_or_404(User, username=username)
        if alvo == request.user:
            return Response({"detail": "Você não pode seguir a si mesmo."}, status=status.HTTP_400_BAD_REQUEST)
        _, criado = Follow.objects.get_or_create(follower=request.user, following=alvo)
        return Response({"following": True}, status=status.HTTP_201_CREATED if criado else status.HTTP_200_OK)

    def delete(self, request, username):
        alvo = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=request.user, following=alvo).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowersView(generics.ListAPIView):
    serializer_class = PublicProfileSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return User.objects.filter(following_set__following=user).order_by("-following_set__created_at")


class FollowingView(generics.ListAPIView):
    serializer_class = PublicProfileSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return User.objects.filter(followers_set__follower=user).order_by("-followers_set__created_at")
