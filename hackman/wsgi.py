"""
WSGI config for hackman project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from gevent import monkey

monkey.patch_all()

from django.core.wsgi import get_wsgi_application  # noqa:E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hackman.settings")

application = get_wsgi_application()
