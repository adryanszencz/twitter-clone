from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Follow, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Perfil", {"fields": ("name", "bio", "avatar")}),)
    list_display = ("username", "name", "email", "is_staff")


admin.site.register(Follow)
