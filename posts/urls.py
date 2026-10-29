from django.urls import include, path
from rest_framework import routers

from posts import api

router = routers.SimpleRouter()
router.register(r"posts", api.PostViewSet, basename="post")

urlpatterns = [
    path("feed/", api.FeedView.as_view(), name="api-feed"),
    path("users/<str:username>/posts/", api.UserPostsView.as_view(), name="api-user-posts"),
    path("", include(router.urls)),
]
