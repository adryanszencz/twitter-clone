from django.contrib import admin

from posts.models import Comment, Like, Post

admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
