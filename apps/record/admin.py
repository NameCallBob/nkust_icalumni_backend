from django.contrib import admin

from apps.record.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """聯絡我們訊息（供管理員後台檢視/標記處理）"""
    list_display = ('name', 'email', 'phone', 'is_handled', 'created_at')
    list_filter = ('is_handled', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_editable = ('is_handled',)
    readonly_fields = ('name', 'email', 'phone', 'message', 'created_at')
    ordering = ('-created_at',)
