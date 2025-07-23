from django.apps import AppConfig


class PostalpinConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'postalpin'
    def ready(self):
        import postalpin.signals