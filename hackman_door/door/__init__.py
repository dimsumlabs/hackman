from django.conf import settings
import importlib


# Hide implementation behind some clever import magic
Door = importlib.import_module(settings.DOOR_LOCK['BACKEND']).Door
