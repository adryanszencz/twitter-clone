from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.factories import PASSWORD, UserFactory
from accounts.models import User


class RegisterTest(APITestCase):
    def test_cadastro_cria_usuario_e_devolve_token(self):
        data = {"username": "adryan", "email": "adryan@email.com", "name": "Adryan", "password": PASSWORD}

        response = self.client.post(reverse("api-register"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="adryan")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(response.json()["token"], Token.objects.get(user=user).key)
        self.assertNotIn("password", response.json()["user"])

    def test_username_repetido_e_recusado(self):
        UserFactory(username="adryan")

        response = self.client.post(reverse("api-register"), {"username": "adryan", "password": PASSWORD})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.json())

    def test_senha_fraca_e_recusada(self):
        response = self.client.post(reverse("api-register"), {"username": "novo", "password": "123"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="novo").exists())


class LoginTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(username="adryan")

    def test_login_devolve_token(self):
        response = self.client.post(reverse("api-login"), {"username": "adryan", "password": PASSWORD})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["token"], Token.objects.get(user=self.user).key)
        self.assertEqual(response.json()["user"]["username"], "adryan")

    def test_senha_errada_da_400(self):
        response = self.client.post(reverse("api-login"), {"username": "adryan", "password": "errada"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_apaga_o_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.post(reverse("api-logout"))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_sem_token_da_401(self):
        response = self.client.post(reverse("api-logout"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
