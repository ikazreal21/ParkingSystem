from django.apps import AppConfig


class ParkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'park'

    def ready(self):
        import park.signals  # Import signals when the app is ready
