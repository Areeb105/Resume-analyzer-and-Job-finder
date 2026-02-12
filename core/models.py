from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    skills = models.JSONField(default=list, blank=True)
    ats_score = models.IntegerField(default=0)
    ats_breakdown = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class SavedJob(models.Model):
    """Model to store saved jobs for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job_id = models.CharField(max_length=255)
    job_title = models.CharField(max_length=500)
    company = models.CharField(max_length=500)
    location = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    redirect_url = models.URLField(max_length=1000, blank=True)
    salary = models.CharField(max_length=200, blank=True)
    posted_date = models.CharField(max_length=100, blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job_id')
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.job_title} at {self.company}"

