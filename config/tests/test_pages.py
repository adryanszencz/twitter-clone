from django.test import TestCase
from django.urls import reverse


class PagesTest(TestCase):
    def test_paginas_abrem(self):
        urls = [
            reverse("feed"),
            reverse("login"),
            reverse("signup"),
            reverse("settings"),
            reverse("people"),
            reverse("post-page", args=[1]),
            reverse("profile", args=["adryan"]),
            reverse("followers-page", args=["adryan"]),
            reverse("following-page", args=["adryan"]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_username_vai_escapado_no_html(self):
        response = self.client.get(reverse("profile", args=['<b>x"']))

        self.assertNotContains(response, '<b>x"')
