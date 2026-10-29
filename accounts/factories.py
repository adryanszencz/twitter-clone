import factory

from accounts.models import User

PASSWORD = "senha-forte-de-teste-123"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"usuario{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@email.com")
    name = factory.Faker("name", locale="pt_BR")
    password = factory.PostGenerationMethodCall("set_password", PASSWORD)

    @factory.post_generation
    def save_password(self, create, extracted, **kwargs):
        if create:
            self.save()
