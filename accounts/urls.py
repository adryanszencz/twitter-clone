from django.urls import path

from accounts import api

urlpatterns = [
    path("auth/register/", api.RegisterView.as_view(), name="api-register"),
    path("auth/login/", api.LoginView.as_view(), name="api-login"),
    path("auth/logout/", api.LogoutView.as_view(), name="api-logout"),
    path("users/me/", api.MeView.as_view(), name="api-me"),
    path("users/me/password/", api.PasswordChangeView.as_view(), name="api-password"),
]
