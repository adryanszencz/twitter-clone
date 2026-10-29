from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.factories import UserFactory
from accounts.models import Follow
from posts.factories import PostFactory
from posts.models import Post


class PostTest(APITestCase):
    def setUp(self):
        self.eu = UserFactory(username="adryan")
        self.client.force_authenticate(self.eu)

    def test_criar_post(self):
        response = self.client.post(reverse("post-list"), {"content": "Meu primeiro tweet"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get()
        self.assertEqual(post.author, self.eu)
        self.assertEqual(response.json()["author"]["username"], "adryan")
        self.assertTrue(response.json()["is_mine"])

    def test_post_vazio_e_recusado(self):
        response = self.client.post(reverse("post-list"), {"content": "   "}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_com_mais_de_280_caracteres_e_recusado(self):
        response = self.client.post(reverse("post-list"), {"content": "a" * 281}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_apagar_o_proprio_post(self):
        post = PostFactory(author=self.eu)

        response = self.client.delete(reverse("post-detail", args=[post.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.exists())

    def test_nao_pode_apagar_post_de_outro(self):
        post = PostFactory()

        response = self.client.delete(reverse("post-detail", args=[post.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.exists())

    def test_posts_de_um_usuario(self):
        ana = UserFactory(username="ana")
        PostFactory.create_batch(2, author=ana)
        PostFactory(author=self.eu)

        data = self.client.get(reverse("api-user-posts", args=["ana"])).json()

        self.assertEqual(data["count"], 2)

    def test_sem_login_da_401(self):
        self.client.force_authenticate(None)

        self.assertEqual(self.client.post(reverse("post-list"), {"content": "oi"}).status_code, 401)


class FeedTest(APITestCase):
    def setUp(self):
        self.eu = UserFactory(username="adryan")
        self.ana = UserFactory(username="ana")
        self.bruno = UserFactory(username="bruno")
        Follow.objects.create(follower=self.eu, following=self.ana)
        self.client.force_authenticate(self.eu)

    def test_feed_mostra_so_quem_eu_sigo(self):
        PostFactory(author=self.ana, content="post da ana")
        PostFactory(author=self.bruno, content="post do bruno")
        PostFactory(author=self.eu, content="meu post")

        data = self.client.get(reverse("api-feed")).json()

        self.assertEqual([p["content"] for p in data["results"]], ["post da ana"])

    def test_feed_do_mais_novo_para_o_mais_antigo(self):
        antigo = PostFactory(author=self.ana)
        novo = PostFactory(author=self.ana)

        data = self.client.get(reverse("api-feed")).json()

        self.assertEqual([p["id"] for p in data["results"]], [novo.id, antigo.id])

    def test_feed_e_paginado(self):
        PostFactory.create_batch(12, author=self.ana)

        data = self.client.get(reverse("api-feed")).json()

        self.assertEqual(data["count"], 12)
        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])

    def test_deixar_de_seguir_tira_do_feed(self):
        PostFactory(author=self.ana)
        Follow.objects.filter(follower=self.eu, following=self.ana).delete()

        self.assertEqual(self.client.get(reverse("api-feed")).json()["count"], 0)
