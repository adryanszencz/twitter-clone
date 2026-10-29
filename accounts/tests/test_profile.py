import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.factories import PASSWORD, UserFactory

MEDIA_TESTE = tempfile.mkdtemp()


def imagem_png(nome="foto.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "blue").save(buffer, "PNG")
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class ProfileTest(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = UserFactory(username="adryan", name="Adryan", bio="Dev")
        self.client.force_authenticate(self.user)

    def test_ver_o_proprio_perfil(self):
        response = self.client.get(reverse("api-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "adryan")

    def test_alterar_so_o_nome_mantem_o_resto(self):
        response = self.client.patch(reverse("api-me"), {"name": "Adryan S."}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Adryan S.")
        self.assertEqual(self.user.bio, "Dev")

    def test_patch_vazio_nao_muda_nada(self):
        response = self.client.patch(reverse("api-me"), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Adryan")

    def test_alterar_a_foto(self):
        response = self.client.patch(reverse("api-me"), {"avatar": imagem_png()}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar.name.startswith("avatars/"))
        self.assertIn("/media/avatars/", response.json()["avatar"])

    def test_arquivo_que_nao_e_imagem_e_recusado(self):
        arquivo = SimpleUploadedFile("foto.png", b"nao sou imagem", content_type="image/png")

        response = self.client.patch(reverse("api-me"), {"avatar": arquivo}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sem_login_da_401(self):
        self.client.force_authenticate(None)

        self.assertEqual(self.client.get(reverse("api-me")).status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_troca_de_senha(self):
        nova = "outra-senha-forte-456"

        response = self.client.post(
            reverse("api-password"), {"current_password": PASSWORD, "new_password": nova}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(nova))
        self.assertNotEqual(response.json()["token"], self.token.key)

    def test_senha_atual_errada(self):
        response = self.client.post(
            reverse("api-password"), {"current_password": "errada", "new_password": "outra-senha-forte-456"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("current_password", response.json())

    def test_senha_nova_fraca(self):
        response = self.client.post(reverse("api-password"), {"current_password": PASSWORD, "new_password": "123"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.json())
