"""
URLs para autenticación de la app accounts
"""

from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"), # Muestra el formulario, valida credenciales y crea la sesión
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]