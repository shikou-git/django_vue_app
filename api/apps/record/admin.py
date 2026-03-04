from django.contrib import admin
from .models import ApiLog


@admin.register(ApiLog)
class ApiLogAdmin(admin.ModelAdmin):
    list_display = ("id", "path", "method", "status_code", "user_id", "ip_address", "created_at")
    list_filter = ("method", "status_code")
    search_fields = ("path", "ip_address", "user_agent")
    readonly_fields = ("path", "method", "status_code", "user", "ip_address", "user_agent", "created_at")
    date_hierarchy = "created_at"
