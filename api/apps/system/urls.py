from django.urls import path

from . import views

urlpatterns = [
    path("get_base_settings/", views.get_base_settings, name="get_base_settings"),
    path("update_base_settings/", views.update_base_settings, name="update_base_settings"),
]
