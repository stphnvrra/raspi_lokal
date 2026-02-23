"""
Django admin configuration for LoKal models.
"""
from django.contrib import admin
from .models import Conversation, Message, SystemSettings


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subject', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'subject', 'created_at']
    search_fields = ['title', 'subject']
    ordering = ['-updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'short_content', 'input_type', 'tts_generated', 'created_at']
    list_filter = ['role', 'input_type', 'tts_generated', 'created_at']
    search_fields = ['content']
    ordering = ['-created_at']

    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = 'Content'


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']
    ordering = ['key']
