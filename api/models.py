"""
Database models for LoKal educational AI backend.
"""
from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """
    Represents a learning session/conversation with a student.
    Groups related messages together.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations',
        null=True,
        blank=True,
        help_text="Student who owns this conversation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(
        max_length=50,
        blank=True,
        help_text="Subject area: Math, Science, English, etc."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this conversation is still active"
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Auto-generated title from first question"
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f"Conversation {self.id} - {self.title or 'Untitled'}"

    def save(self, *args, **kwargs):
        # Auto-generate title from first message if not set
        if not self.title and self.pk:
            first_message = self.messages.filter(role='user').first()
            if first_message:
                self.title = first_message.content[:50] + ('...' if len(first_message.content) > 50 else '')
        super().save(*args, **kwargs)


class Message(models.Model):
    """
    Individual message in a conversation (either from user or AI assistant).
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    INPUT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('voice', 'Voice'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )
    content = models.TextField(
        help_text="The message content"
    )
    input_type = models.CharField(
        max_length=10,
        choices=INPUT_TYPE_CHOICES,
        default='text',
        help_text="How the message was input (text or voice)"
    )
    audio_input_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path to original audio input file (for voice messages)"
    )
    audio_output_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path to TTS audio output file"
    )
    tts_generated = models.BooleanField(
        default=False,
        help_text="Whether TTS audio has been generated for this message"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class SystemSettings(models.Model):
    """
    Key-value store for system-wide settings.
    Allows runtime configuration without code changes.
    """
    key = models.CharField(
        max_length=50,
        unique=True,
        help_text="Setting key name"
    )
    value = models.TextField(
        help_text="Setting value (stored as string, parsed as needed)"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Human-readable description of this setting"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    @classmethod
    def get_value(cls, key, default=None):
        """Get a setting value by key, with optional default."""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, key, value, description=''):
        """Set or update a setting value."""
        setting, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': str(value), 'description': description}
        )
        return setting
