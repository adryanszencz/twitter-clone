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


class Follow(models.Model):
    """follower segue following."""

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow"),
            models.CheckConstraint(condition=~models.Q(follower=models.F("following")), name="no_self_follow"),
        ]

    def __str__(self):
        return f"{self.follower} segue {self.following}"
