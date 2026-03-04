from django.urls import path

from . import views

urlpatterns = [
    path("get_apilog_list/", views.get_apilog_list, name="get_apilog_list"),
    path("get_apistats/", views.get_api_stats, name="get_apistats"),
    path("export_apilog/", views.export_apilog, name="export_apilog"),
    path("delete_apilog/", views.delete_apilog, name="delete_apilog"),
    path("batch_delete_apilog/", views.batch_delete_apilog, name="batch_delete_apilog"),
    path("get_filter_options/", views.get_filter_options, name="get_filter_options"),
]
