from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("shorten/", views.shorten_view, name="shorten"),
    path("urls/", views.url_list_view, name="url_list"),
    path("delete/<int:url_id>/", views.delete_url_view, name="delete_url"),
    path("logout/", views.logout_view, name="logout"),
    path("generate-qr/", views.generate_qr_view, name="generate_qr"),
    path("qr-list/", views.qr_list_view, name="qr_list"),
    path("dashborad/", views.dashboard_view, name="dashboard"),
    path('export-urls/', views.export_csv_view, name='export_urls'),
]
