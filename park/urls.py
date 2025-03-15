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

    path('calendar/', views.calendar_view, name="calendar"),
    path('reservation_date/<str:selected_date>', views.reservations_by_date, name="reservations_by_date"),
    path('reservation_spot/<str:pk>', views.reservations_by_spot, name="reservation_spot"),

    # pwa
    url(r'^serviceworker\.js$', service_worker, name='serviceworker'),
    url(r'^manifest\.json$', manifest, name='manifest'),
    url('^offline/$', offline, name='offline'),

    path(".well-known/assetlinks.json", views.AssetLink),

    # Scan
    path("scan_to_occupy/<str:pk>", views.scan_to_occupy, name="scan_to_occupy"),

    # Additional
    path("parked", views.you_are_now_parked, name="you_are_now_parked"),
    path("not_parked", views.not_in_schedule, name="not_in_schedule"),
    path("exceed_time", views.exceed_time, name="exceed_time"),

    # Terms and Conditions
    path("terms/", views.termsandconditions, name="terms"),


    # Auth
    path("login/", views.Login, name="login"),
    path("register/", views.Register, name="register"),
    path("logout/", views.Logout, name="logout"),

    # Dashboard
    path("dashboard/", views.Dashboard, name="dashboard"),

    # Email Verification
    path("verify_email/<str:verification_code>", views.VerifyEmail, name="verify_email"),
    path("need_verification/", views.NeedVerification, name="need_verification"),

    # Profile
    path("user_profile/", views.UserProfile, name="user_profile"),
]