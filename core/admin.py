from django.contrib import admin
from .models import SavedJob, UserProfile

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'company', 'location', 'posted_date', 'saved_at')
    search_fields = ('job_title', 'company', 'location')
    list_filter = ('saved_at', 'posted_date')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'ats_score', 'uploaded_at')
    search_fields = ('user__username', 'user__email')
