from django.contrib import admin
from apps.member.models import Member, Graduate, Position, OutstandingAlumni, SchoolOutstandingAlumni


class OutstandingAlumniAdmin(admin.ModelAdmin):
    list_display = ['member', 'highlight', 'is_featured', 'date_awarded', 'sort_order']
    list_filter = ['is_featured', 'date_awarded']
    search_fields = ['member__name', 'highlight', 'achievements']
    ordering = ['sort_order', '-date_awarded']
    list_editable = ['sort_order', 'is_featured']


class SchoolOutstandingAlumniAdmin(admin.ModelAdmin):
    list_display = ['member', 'highlight', 'is_featured', 'date_awarded', 'sort_order']
    list_filter = ['is_featured', 'date_awarded']
    search_fields = ['member__name', 'highlight', 'achievements']
    ordering = ['sort_order', '-date_awarded']
    list_editable = ['sort_order', 'is_featured']


admin.site.register(Member)
admin.site.register(Graduate)
admin.site.register(Position)
admin.site.register(OutstandingAlumni, OutstandingAlumniAdmin)
admin.site.register(SchoolOutstandingAlumni, SchoolOutstandingAlumniAdmin)