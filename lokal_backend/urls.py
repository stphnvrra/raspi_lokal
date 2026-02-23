"""
URL configuration for LoKal backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse
from pathlib import Path

from django.views.decorators.csrf import ensure_csrf_cookie

# Frontend file serving views
@ensure_csrf_cookie
def serve_index(request):
    return FileResponse(open(settings.BASE_DIR / 'index.html', 'rb'), content_type='text/html')

def serve_script(request):
    return FileResponse(open(settings.BASE_DIR / 'script.js', 'rb'), content_type='application/javascript')

def serve_style(request):
    return FileResponse(open(settings.BASE_DIR / 'style.css', 'rb'), content_type='text/css')

def serve_logo(request):
    return FileResponse(open(settings.BASE_DIR / 'logo.png', 'rb'), content_type='image/png')

@ensure_csrf_cookie
def serve_login(request):
    return FileResponse(open(settings.BASE_DIR / 'login.html', 'rb'), content_type='text/html')

@ensure_csrf_cookie
def serve_register(request):
    return FileResponse(open(settings.BASE_DIR / 'register.html', 'rb'), content_type='text/html')

@ensure_csrf_cookie
def serve_change_password(request):
    return FileResponse(open(settings.BASE_DIR / 'change_password.html', 'rb'), content_type='text/html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Serve frontend files
    path('', serve_index, name='index'),
    path('index.html', serve_index, name='index_html'),
    path('login.html', serve_login, name='login'),
    path('register.html', serve_register, name='register'),
    path('change_password.html', serve_change_password, name='change_password'),
    path('script.js', serve_script, name='script'),
    path('style.css', serve_style, name='style'),
    path('logo.png', serve_logo, name='logo'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

