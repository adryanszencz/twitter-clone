"""Páginas do front-end. Cada página é um template que consome a API REST (/api/) com JavaScript."""

from django.shortcuts import render


def feed(request):
    return render(request, "feed.html", {"active": "feed"})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def settings_page(request):
    return render(request, "settings.html", {"active": "settings"})


def profile(request, username):
    return render(request, "profile.html", {"username": username})


def people(request, username=None, mode="search"):
    titulos = {"search": "Pessoas", "followers": f"Seguidores de @{username}", "following": f"@{username} segue"}
    return render(request, "people.html", {
        "active": "people" if mode == "search" else "profile",
        "heading": titulos[mode],
        "mode": mode,
        "username": username,
    })


def post_detail(request, post_id):
    return render(request, "post_detail.html", {"post_id": post_id})
