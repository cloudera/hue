from django.apps import AppConfig


class DjangoSaml2Config(AppConfig):
    name = "djangosaml2"
    verbose_name = "DjangoSAML2"

    def ready(self):
        from . import signals  # noqa
