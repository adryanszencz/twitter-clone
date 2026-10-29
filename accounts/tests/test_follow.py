from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.factories import UserFactory
from accounts.models import Follow


class FollowTest(APITestCase):
    def setUp(self):
        self.eu = UserFactory(username="adryan")
        self.ana = UserFactory(username="ana", name="Ana Souza")
        self.bruno = UserFactory(username="bruno")
        self.client.force_authenticate(self.eu)

    def test_seguir(self):
        response = self.client.post(reverse("api-follow", args=["ana"]))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(follower=self.eu, following=self.ana).exists())

    def test_seguir_duas_vezes_nao_duplica(self):
        self.client.post(reverse("api-follow", args=["ana"]))

        response = self.client.post(reverse("api-follow", args=["ana"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Follow.objects.count(), 1)

    def test_nao_pode_seguir_a_si_mesmo(self):
        response = self.client.post(reverse("api-follow", args=["adryan"]))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Follow.objects.exists())

    def test_deixar_de_seguir(self):
        Follow.objects.create(follower=self.eu, following=self.ana)

        response = self.client.delete(reverse("api-follow", args=["ana"]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Follow.objects.exists())

    def test_usuario_inexistente_da_404(self):
        self.assertEqual(self.client.post(reverse("api-follow", args=["ninguem"])).status_code, 404)

    def test_listas_de_seguidores_e_seguidos(self):
        Follow.objects.create(follower=self.eu, following=self.ana)
        Follow.objects.create(follower=self.bruno, following=self.eu)

        seguidos = self.client.get(reverse("api-following", args=["adryan"])).json()
        seguidores = self.client.get(reverse("api-followers", args=["adryan"])).json()

        self.assertEqual([u["username"] for u in seguidos["results"]], ["ana"])
        self.assertEqual([u["username"] for u in seguidores["results"]], ["bruno"])

    def test_perfil_publico_mostra_contadores_e_se_eu_sigo(self):
        Follow.objects.create(follower=self.eu, following=self.ana)
        Follow.objects.create(follower=self.bruno, following=self.ana)

        data = self.client.get(reverse("api-profile", args=["ana"])).json()

        self.assertEqual(data["followers_count"], 2)
        self.assertEqual(data["following_count"], 0)
        self.assertTrue(data["is_following"])
        self.assertEqual(data["display_name"], "Ana Souza")

    def test_busca_de_usuarios(self):
        data = self.client.get(reverse("api-users"), {"search": "souza"}).json()

        self.assertEqual([u["username"] for u in data["results"]], ["ana"])

    def test_busca_nao_mostra_o_proprio_usuario(self):
        data = self.client.get(reverse("api-users")).json()

        self.assertNotIn("adryan", [u["username"] for u in data["results"]])

    def test_sem_login_da_401(self):
        self.client.force_authenticate(None)

        self.assertEqual(self.client.post(reverse("api-follow", args=["ana"])).status_code, 401)
