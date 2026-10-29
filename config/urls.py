from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("posts.urls")),
    path("api/", include("accounts.urls")),
    # front-end (templates que consomem a API)
    path("", views.feed, name="feed"),
    path("login/", views.login, name="login"),
    path("cadastro/", views.signup, name="signup"),
    path("configuracoes/", views.settings_page, name="settings"),
    path("pessoas/", views.people, name="people"),
    path("post/<int:post_id>/", views.post_detail, name="post-page"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/seguidores/", views.people, {"mode": "followers"}, name="followers-page"),
    path("u/<str:username>/seguindo/", views.people, {"mode": "following"}, name="following-page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
