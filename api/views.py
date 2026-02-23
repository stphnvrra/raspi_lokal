"""
API views for LoKal educational AI backend.
"""
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message, SystemSettings
from .serializers import (
    AskQuestionSerializer,
    AskVoiceSerializer,
    AskResponseSerializer,
    TTSSerializer,
    ConversationSerializer,
    ConversationListSerializer,
    SystemSettingsSerializer,
    HealthCheckSerializer,
)
from .services.ollama_service import ollama_service
from .services.tts_service import tts_service
from .services.stt_service import stt_service

logger = logging.getLogger(__name__)


# ========================================
# Authentication Views
# ========================================

class RegisterView(APIView):
    """
    Register a new student account.
    POST /api/auth/register/
    """

    def post(self, request):
        """Create a new user account."""
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        # Validation
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already taken'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        logger.info(f"New user registered: {username}")

        return Response({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Login with username and password.
    POST /api/auth/login/
    """

    def post(self, request):
        """Authenticate user and start session."""
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            logger.info(f"User logged in: {username}")
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                }
            })
        else:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    Logout current user.
    POST /api/auth/logout/
    """

    def post(self, request):
        """End user session."""
        if request.user.is_authenticated:
            logger.info(f"User logged out: {request.user.username}")
        logout(request)
        return Response({'message': 'Logged out successfully'})


class CurrentUserView(APIView):
    """
    Get current authenticated user info.
    GET /api/auth/user/
    """

    def get(self, request):
        """Return current user info or unauthenticated status."""
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                }
            })
        else:
            return Response({
                'authenticated': False,
                'user': None
            })


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    POST /api/auth/change-password/
    """

    def post(self, request):
        """Update user password."""
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {'error': 'You must be logged in to change your password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        # Validation
        if not old_password:
            return Response(
                {'error': 'Old password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not new_password:
            return Response(
                {'error': 'New password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not confirm_password:
            return Response(
                {'error': 'Password confirmation is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(new_password) < 8:
            return Response(
                {'error': 'New password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if new_password != confirm_password:
            return Response(
                {'error': 'New passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if old_password == new_password:
            return Response(
                {'error': 'New password must be different from the old password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify old password
        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        request.user.set_password(new_password)
        request.user.save()

        logger.info(f"Password changed for user: {request.user.username}")

        return Response({
            'message': 'Password changed successfully'
        })


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring.
    GET /api/health/
    """

    def get(self, request):
        """Return health status of all services."""
        health = {
            'status': 'healthy',
            'database': 'connected',
            'ollama': 'available' if ollama_service.is_available() else 'unavailable',
            'tts': 'available' if tts_service.is_available else 'unavailable',
            'stt': 'available' if stt_service.is_available else 'unavailable',
            'timestamp': datetime.now().isoformat(),
        }
        
        # Check database
        try:
            Conversation.objects.count()
        except Exception:
            health['database'] = 'error'
            health['status'] = 'degraded'
        
        # Update overall status
        if health['ollama'] == 'unavailable':
            health['status'] = 'degraded'
        
        return Response(health)


class AskQuestionView(APIView):
    """
    Submit a text question and get AI response.
    POST /api/ask/
    """

    def post(self, request):
        """Process a text question and return AI response."""
        serializer = AskQuestionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        conversation_id = serializer.validated_data.get('conversation_id')
        subject = serializer.validated_data.get('subject', '')
        enable_tts = serializer.validated_data.get('enable_tts', False)
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create conversation associated with current user if authenticated
            conversation = Conversation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                subject=subject,
                title=question[:50] + ('...' if len(question) > 50 else '')
            )
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=question,
            input_type='text'
        )
        
        # Build conversation history for context
        history = list(
            conversation.messages
            .exclude(id=user_message.id)
            .values('role', 'content')
            .order_by('created_at')
        )[-10:]  # Limit history to last 10 messages
        
        # Get AI response
        answer = ollama_service.chat(
            message=question,
            conversation_history=history,
            subject=subject or conversation.subject
        )
        
        # Save assistant message
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=answer
        )
        
        # Generate TTS if requested
        audio_url = None
        if enable_tts:
            audio_path = tts_service.generate_audio_file(answer)
            if audio_path:
                assistant_message.audio_output_path = audio_path
                assistant_message.tts_generated = True
                assistant_message.save()
                audio_url = f"{settings.MEDIA_URL}{audio_path}"
        
        # Update conversation timestamp
        conversation.save()
        
        response_data = {
            'answer': answer,
            'conversation_id': conversation.id,
            'message_id': assistant_message.id,
            'audio_url': audio_url,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class AskVoiceView(APIView):
    """
    Submit voice audio and get AI response.
    POST /api/ask/voice/
    """

    def post(self, request):
        """Process voice input and return AI response."""
        serializer = AskVoiceSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = serializer.validated_data['audio']
        conversation_id = serializer.validated_data.get('conversation_id')
        subject = serializer.validated_data.get('subject', '')
        enable_tts = serializer.validated_data.get('enable_tts', True)
        
        # Save uploaded audio
        audio_path = stt_service.save_uploaded_audio(audio_file)
        
        # Transcribe audio to text
        transcribed_text, success = stt_service.transcribe_file(audio_path)
        
        if not success:
            return Response(
                {'error': transcribed_text},  # Error message
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            conversation = Conversation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                subject=subject,
                title=transcribed_text[:50] + ('...' if len(transcribed_text) > 50 else '')
            )
        
        # Save user message with audio path
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=transcribed_text,
            input_type='voice',
            audio_input_path=audio_path
        )
        
        # Build conversation history
        history = list(
            conversation.messages
            .exclude(id=user_message.id)
            .values('role', 'content')
            .order_by('created_at')
        )[-10:]
        
        # Get AI response
        answer = ollama_service.chat(
            message=transcribed_text,
            conversation_history=history,
            subject=subject or conversation.subject
        )
        
        # Save assistant message
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=answer
        )
        
        # Generate TTS (default enabled for voice interactions)
        audio_url = None
        if enable_tts:
            audio_output_path = tts_service.generate_audio_file(answer)
            if audio_output_path:
                assistant_message.audio_output_path = audio_output_path
                assistant_message.tts_generated = True
                assistant_message.save()
                audio_url = f"{settings.MEDIA_URL}{audio_output_path}"
        
        conversation.save()
        
        response_data = {
            'answer': answer,
            'conversation_id': conversation.id,
            'message_id': assistant_message.id,
            'audio_url': audio_url,
            'transcribed_question': transcribed_text,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class TTSView(APIView):
    """
    Convert text to speech audio.
    POST /api/tts/
    """

    def post(self, request):
        """Generate TTS audio from text."""
        serializer = TTSSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text = serializer.validated_data['text']
        message_id = serializer.validated_data.get('message_id')
        
        # Generate audio file
        audio_path = tts_service.generate_audio_file(text)
        
        if not audio_path:
            return Response(
                {'error': 'Failed to generate audio. TTS service may be unavailable.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update message if ID provided
        if message_id:
            try:
                message = Message.objects.get(id=message_id)
                message.audio_output_path = audio_path
                message.tts_generated = True
                message.save()
            except Message.DoesNotExist:
                pass  # Ignore if message not found
        
        return Response({
            'audio_url': f"{settings.MEDIA_URL}{audio_path}",
            'message': 'Audio generated successfully'
        })


class STTView(APIView):
    """
    Convert speech audio to text.
    POST /api/stt/
    
    Accepts audio file upload and returns transcribed text.
    Supports WebM (browser format), WAV, OGG, MP3, and other formats.
    """

    def post(self, request):
        """Transcribe audio to text."""
        # Check if audio file is provided
        if 'audio' not in request.FILES:
            return Response(
                {'error': 'No audio file provided. Upload a file with key "audio".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['audio']
        
        # Check if STT service is available
        if not stt_service.is_available:
            return Response(
                {'error': 'Speech recognition is not available. Vosk model may not be installed.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            # Save uploaded audio
            audio_path = stt_service.save_uploaded_audio(audio_file)
            
            # Transcribe audio to text
            transcribed_text, success = stt_service.transcribe_file(audio_path)
            
            if success:
                return Response({
                    'text': transcribed_text,
                    'success': True
                })
            else:
                return Response({
                    'text': transcribed_text,  # Contains error message
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"STT processing failed: {e}")
            return Response(
                {'error': f'Speech recognition failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationListView(APIView):
    """
    List all conversations.
    GET /api/conversations/
    """

    def get(self, request):
        """Return list of conversations for current user."""
        # Filter by user if authenticated
        if request.user.is_authenticated:
            conversations = Conversation.objects.filter(user=request.user)
        else:
            conversations = Conversation.objects.filter(user__isnull=True)
        
        # Filter by active status if specified
        is_active = request.query_params.get('active')
        if is_active is not None:
            conversations = conversations.filter(is_active=is_active.lower() == 'true')
        
        # Filter by subject if specified
        subject = request.query_params.get('subject')
        if subject:
            conversations = conversations.filter(subject__icontains=subject)
        
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new conversation."""
        subject = request.data.get('subject', '')
        title = request.data.get('title', '')
        
        conversation = Conversation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            subject=subject,
            title=title
        )
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationDetailView(APIView):
    """
    Get, update, or delete a specific conversation.
    GET/PUT/DELETE /api/conversations/{id}/
    """

    def get(self, request, pk):
        """Get conversation with all messages."""
        try:
            conversation = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update conversation details."""
        try:
            conversation = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update allowed fields
        if 'title' in request.data:
            conversation.title = request.data['title']
        if 'subject' in request.data:
            conversation.subject = request.data['subject']
        if 'is_active' in request.data:
            conversation.is_active = request.data['is_active']
        
        conversation.save()
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)

    def delete(self, request, pk):
        """Delete a conversation and all its messages."""
        try:
            conversation = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SystemSettingsView(APIView):
    """
    Get or update system settings.
    GET/PUT /api/settings/
    """

    def get(self, request):
        """Get all system settings."""
        settings = SystemSettings.objects.all()
        serializer = SystemSettingsSerializer(settings, many=True)
        return Response(serializer.data)

    def put(self, request):
        """Update or create system settings."""
        if not isinstance(request.data, dict):
            return Response(
                {'error': 'Request body must be a JSON object'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_settings = []
        for key, value in request.data.items():
            if isinstance(value, dict):
                setting = SystemSettings.set_value(
                    key=key,
                    value=value.get('value', ''),
                    description=value.get('description', '')
                )
            else:
                setting = SystemSettings.set_value(key=key, value=value)
            updated_settings.append(setting)
        
        serializer = SystemSettingsSerializer(updated_settings, many=True)
        return Response(serializer.data)


class SpeakView(APIView):
    """
    Speak text directly through connected speaker.
    POST /api/speak/
    """

    def post(self, request):
        """Speak text through speaker (blocking)."""
        text = request.data.get('text', '')
        
        if not text:
            return Response(
                {'error': 'Text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = tts_service.speak(text)
        
        if success:
            return Response({'message': 'Speech completed'})
        else:
            return Response(
                {'error': 'Failed to speak. TTS service may be unavailable.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OllamaModelsView(APIView):
    """
    Get available Ollama models.
    GET /api/ollama/models/
    """

    def get(self, request):
        """List available Ollama models."""
        models = ollama_service.get_available_models()
        current_model = getattr(settings, 'OLLAMA_MODEL', 'tinyllama')
        
        return Response({
            'current_model': current_model,
            'available_models': models,
            'ollama_available': ollama_service.is_available()
        })
