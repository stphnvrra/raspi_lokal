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

from django.shortcuts import render

# Frontend file serving views
@ensure_csrf_cookie
def serve_index(request):
    return render(request, 'index.html')

@ensure_csrf_cookie
def serve_login(request):
    return render(request, 'login.html')

@ensure_csrf_cookie
def serve_register(request):
    return render(request, 'register.html')

@ensure_csrf_cookie
def serve_change_password(request):
    return render(request, 'change_password.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Serve frontend templates
    path('', serve_index, name='index'),
    path('index.html', serve_index, name='index_html'),
    path('login.html', serve_login, name='login'),
    path('register.html', serve_register, name='register'),
    path('change_password.html', serve_change_password, name='change_password'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

