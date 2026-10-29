import factory

from accounts.factories import UserFactory
from posts.models import Post


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    content = factory.Faker("sentence", nb_words=10, locale="pt_BR")
