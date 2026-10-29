import factory

from accounts.factories import UserFactory
from posts.models import Comment, Post


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    content = factory.Faker("sentence", nb_words=10, locale="pt_BR")


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    content = factory.Faker("sentence", nb_words=6, locale="pt_BR")
