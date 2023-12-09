from django.apps import AppConfig


class RedeggConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "redegg"

    # This is where you import your signals if you need any
    def ready(self):
        import redegg.signals
