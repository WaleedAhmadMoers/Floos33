from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # noqa: F401
        from . import signals  # register signals
    verbose_name = "Core"
