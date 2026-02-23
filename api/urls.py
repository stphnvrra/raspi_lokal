"""
URL configuration for LoKal API endpoints.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health check
    path('health/', views.HealthCheckView.as_view(), name='health'),
    
    # Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/user/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Question endpoints
    path('ask/', views.AskQuestionView.as_view(), name='ask'),
    path('ask/voice/', views.AskVoiceView.as_view(), name='ask-voice'),
    
    # Text-to-speech
    path('tts/', views.TTSView.as_view(), name='tts'),
    path('speak/', views.SpeakView.as_view(), name='speak'),
    
    # Speech-to-text
    path('stt/', views.STTView.as_view(), name='stt'),
    
    # Conversations
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    
    # System settings
    path('settings/', views.SystemSettingsView.as_view(), name='settings'),
    
    # Ollama info
    path('ollama/models/', views.OllamaModelsView.as_view(), name='ollama-models'),
]
