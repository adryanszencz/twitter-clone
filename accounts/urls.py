from django.urls import path

from accounts import api, follow_api

urlpatterns = [
    path("auth/register/", api.RegisterView.as_view(), name="api-register"),
    path("auth/login/", api.LoginView.as_view(), name="api-login"),
    path("auth/logout/", api.LogoutView.as_view(), name="api-logout"),
    path("users/", follow_api.UserSearchView.as_view(), name="api-users"),
    path("users/me/", api.MeView.as_view(), name="api-me"),
    path("users/me/password/", api.PasswordChangeView.as_view(), name="api-password"),
    path("users/<str:username>/", follow_api.PublicProfileView.as_view(), name="api-profile"),
    path("users/<str:username>/follow/", follow_api.FollowView.as_view(), name="api-follow"),
    path("users/<str:username>/followers/", follow_api.FollowersView.as_view(), name="api-followers"),
    path("users/<str:username>/following/", follow_api.FollowingView.as_view(), name="api-following"),
]
