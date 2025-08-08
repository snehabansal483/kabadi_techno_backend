from django.apps import AppConfig


class EmployeeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "employee"
    def ready(self):
        from .models import delete_employee_related_user
