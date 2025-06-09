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
    path("done_parking", views.done_parking, name="done_parking"),

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

    # Logistics and Summary
    path('logistics/', views.logistics_view, name='logistics'),
    path('summary/', views.summary_view, name='summary'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin Dashboard URLs
    path('admins/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admins/reservations/', views.admin_reservations, name='admin_reservations'),
    path('admins/reservations/<uuid:reservation_id>/', views.admin_reservation_detail, name='admin_reservation_detail'),
    path('admins/parked/', views.admin_parked, name='admin_parked'),
    path('admins/parked/<uuid:parked_id>/', views.admin_parked_detail, name='admin_parked_detail'),
    path('admins/logistics/', views.admin_logistics, name='admin_logistics'),
    path('admins/summaries/', views.admin_summaries, name='admin_summaries'),
    path('admins/users/', views.admin_users, name='admin_users'),
    # path('admins/settings/', views.admin_settings, name='admin_settings'),
    path('reservations/<uuid:reservation_id>/download/', views.download_reservation_pdf, name='download_reservation_pdf'),
]