from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.factories import UserFactory
from accounts.models import Follow
from posts.factories import CommentFactory, PostFactory
from posts.models import Comment, Like


class LikeTest(APITestCase):
    def setUp(self):
        self.eu = UserFactory(username="adryan")
        self.post = PostFactory()
        self.client.force_authenticate(self.eu)

    def test_curtir(self):
        response = self.client.post(reverse("post-like", args=[self.post.id]))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"liked": True, "likes_count": 1})

    def test_curtir_duas_vezes_conta_uma(self):
        self.client.post(reverse("post-like", args=[self.post.id]))

        response = self.client.post(reverse("post-like", args=[self.post.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 1)

    def test_descurtir(self):
        Like.objects.create(user=self.eu, post=self.post)

        response = self.client.delete(reverse("post-like", args=[self.post.id]))

        self.assertEqual(response.json(), {"liked": False, "likes_count": 0})

    def test_post_mostra_contador_e_se_eu_curti(self):
        Like.objects.create(user=self.eu, post=self.post)
        Like.objects.create(user=UserFactory(), post=self.post)

        data = self.client.get(reverse("post-detail", args=[self.post.id])).json()

        self.assertEqual(data["likes_count"], 2)
        self.assertTrue(data["liked_by_me"])

    def test_feed_traz_curtidas_e_comentarios(self):
        Follow.objects.create(follower=self.eu, following=self.post.author)
        Like.objects.create(user=UserFactory(), post=self.post)
        CommentFactory.create_batch(3, post=self.post)

        post = self.client.get(reverse("api-feed")).json()["results"][0]

        self.assertEqual(post["likes_count"], 1)
        self.assertEqual(post["comments_count"], 3)
        self.assertFalse(post["liked_by_me"])

    def test_curtir_post_inexistente_da_404(self):
        self.assertEqual(self.client.post(reverse("post-like", args=[999])).status_code, 404)


class CommentTest(APITestCase):
    def setUp(self):
        self.eu = UserFactory(username="adryan")
        self.post = PostFactory()
        self.client.force_authenticate(self.eu)

    def test_comentar(self):
        response = self.client.post(reverse("post-comments", args=[self.post.id]), {"content": "Concordo!"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comentario = Comment.objects.get()
        self.assertEqual(comentario.author, self.eu)
        self.assertEqual(comentario.post, self.post)

    def test_comentario_vazio_e_recusado(self):
        response = self.client.post(reverse("post-comments", args=[self.post.id]), {"content": " "})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_comentarios_do_mais_antigo_ao_mais_novo(self):
        primeiro = CommentFactory(post=self.post)
        segundo = CommentFactory(post=self.post)
        CommentFactory()  # comentário de outro post

        data = self.client.get(reverse("post-comments", args=[self.post.id])).json()

        self.assertEqual([c["id"] for c in data["results"]], [primeiro.id, segundo.id])

    def test_apagar_o_proprio_comentario(self):
        comentario = CommentFactory(author=self.eu, post=self.post)

        response = self.client.delete(reverse("comment-detail", args=[comentario.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.exists())

    def test_nao_pode_apagar_comentario_de_outro(self):
        comentario = CommentFactory(post=self.post)

        response = self.client.delete(reverse("comment-detail", args=[comentario.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
