from django.contrib.auth import views as auth_views

from django.urls import path
from . import views




urlpatterns = [
    path("", views.LandingPage, name="landing"),
    path("about/", views.About, name="about"),
    path("services/", views.Services, name="services"),
    path("reviews/", views.Reviews, name="reviews"),

    # Auth
    path("login/", views.Login, name="login"),
    path("register/", views.Register, name="register"),
    path("logout/", views.Logout, name="logout"),

    # Dashboard
    path("dashboard/", views.Dashboard, name="dashboard"),
]