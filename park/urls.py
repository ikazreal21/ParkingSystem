from django.contrib.auth import views as auth_views

from django.urls import path
from . import views

from django.urls import re_path as url
from pwa.views import manifest, service_worker, offline




urlpatterns = [
    path("", views.LandingPage, name="landing"),
    path("about/", views.About, name="about"),
    path("services/", views.Services, name="services"),
    path("reviews/", views.Reviews, name="reviews"),

    # Park
    path('dasboard/', views.Dashboard, name="dasboard"),
    path('available/', views.parking_spots, name="available"),
    path('current/', views.parked_vehicles, name="current"),
    path('reserved/', views.reservations, name="reserved"),
    path('reserve_spot/', views.reserve_spot, name="reserve_spot"),
    path('view_qr/<str:reservation_id>', views.view_qr, name='view_qr'),
    # path('history/', views.History, name="history"),

    # pwa
    url(r'^serviceworker\.js$', service_worker, name='serviceworker'),
    url(r'^manifest\.json$', manifest, name='manifest'),
    url('^offline/$', offline, name='offline'),

    path(".well-known/assetlinks.json", views.AssetLink),

    # Auth
    path("login/", views.Login, name="login"),
    path("register/", views.Register, name="register"),
    path("logout/", views.Logout, name="logout"),

    # Dashboard
    path("dashboard/", views.Dashboard, name="dashboard"),
]