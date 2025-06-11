from django.apps import AppConfig
from dltik.flags import FlagManager

FlagManager.clear()

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dltik'

    def ready(self):
        FlagManager.clear()