from django.contrib import admin
from .models import Job, Application
from django.utils.html import format_html


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'job', 'status', 'video_resume', 'ai_sentiment', 'video_preview')
    list_filter = ('status', 'job', 'applied_at')
    search_fields = ('name', 'email')
    list_editable = ('status',)
    readonly_fields = ('video_resume',)

    def video_preview(self, obj):
        if obj.video_resume:
            return format_html('<a href="{}" target="_blank">🎥 View Video</a>', obj.video_resume.url)
        return "No Video"
    
    video_preview.short_description = "Video Resume"


admin.site.register(Job)
admin.site.register(Application, ApplicationAdmin)
