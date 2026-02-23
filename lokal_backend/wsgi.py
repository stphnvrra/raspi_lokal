"""
WSGI config for LoKal backend.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lokal_backend.settings')

application = get_wsgi_application()
