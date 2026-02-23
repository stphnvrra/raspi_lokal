"""
Django REST Framework serializers for LoKal API.
"""
from rest_framework import serializers
from .models import Conversation, Message, SystemSettings


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    class Meta:
        model = Message
        fields = [
            'id', 'role', 'content', 'input_type',
            'audio_output_path', 'tts_generated', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages."""
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'subject', 'is_active',
            'created_at', 'updated_at', 'message_count', 'messages'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing conversations (without messages)."""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'subject', 'is_active',
            'created_at', 'updated_at', 'message_count', 'last_message'
        ]

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100] + ('...' if len(last_msg.content) > 100 else ''),
                'created_at': last_msg.created_at
            }
        return None


class AskQuestionSerializer(serializers.Serializer):
    """Serializer for the /api/ask/ endpoint."""
    question = serializers.CharField(
        max_length=5000,
        help_text="The question to ask the AI"
    )
    conversation_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional: ID of existing conversation to continue"
    )
    subject = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Optional: Subject area (Math, Science, etc.)"
    )
    enable_tts = serializers.BooleanField(
        default=False,
        help_text="Whether to generate TTS audio for the response"
    )


class AskVoiceSerializer(serializers.Serializer):
    """Serializer for the /api/ask/voice/ endpoint."""
    audio = serializers.FileField(
        help_text="Audio file containing the spoken question"
    )
    conversation_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional: ID of existing conversation to continue"
    )
    subject = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Optional: Subject area"
    )
    enable_tts = serializers.BooleanField(
        default=True,  # Default to True for voice interactions
        help_text="Whether to generate TTS audio for the response"
    )


class TTSSerializer(serializers.Serializer):
    """Serializer for the /api/tts/ endpoint."""
    text = serializers.CharField(
        max_length=10000,
        help_text="Text to convert to speech"
    )
    message_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional: Message ID to associate with generated audio"
    )


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SystemSettings model."""
    
    class Meta:
        model = SystemSettings
        fields = ['key', 'value', 'description', 'updated_at']
        read_only_fields = ['updated_at']


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response."""
    status = serializers.CharField()
    database = serializers.CharField()
    ollama = serializers.CharField()
    timestamp = serializers.DateTimeField()


class AskResponseSerializer(serializers.Serializer):
    """Serializer for AI response."""
    answer = serializers.CharField()
    conversation_id = serializers.IntegerField()
    message_id = serializers.IntegerField()
    audio_url = serializers.CharField(required=False, allow_null=True)
    transcribed_question = serializers.CharField(required=False, allow_null=True)
