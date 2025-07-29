

from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    application_link = models.URLField(blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



     
class Application(models.Model):  
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Applied', 'Applied'),
        ('Reviewed', 'Reviewed'),
        ('Interview', 'Interview'),
        ('Offered', 'Offered'),
        ('Rejected', 'Rejected'),
    ]   
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    video_resume = models.FileField(upload_to='video_resumes/', blank=True, null=True)  # 🎥 New field
    ai_sentiment = models.CharField(max_length=50, blank=True, null=True)  # ✅ Store AI result
    ai_score = models.FloatField(blank=True, null=True) 
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    


    def __str__(self):
        return f"{self.name} - {self.job.title}"

