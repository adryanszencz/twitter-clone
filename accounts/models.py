from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuário do clone: além do username, tem nome de exibição, bio e foto de perfil."""

    name = models.CharField("nome", max_length=50, blank=True)
    bio = models.CharField(max_length=160, blank=True)
    avatar = models.ImageField("foto de perfil", upload_to="avatars/", blank=True)

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        return self.name or self.username
