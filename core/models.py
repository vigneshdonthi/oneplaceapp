from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date




# Task Model
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    due_time = models.TimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_completed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Habit Model
class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default="✅")  # Optional: Emoji/Icon
    days = models.JSONField(default=list)  # e.g., ["Mon", "Wed", "Fri"]

    # Tracking fields
    is_done_today = models.BooleanField(default=False)
    last_checkin = models.DateField(default=date.today)
    streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)

    # Weekly progress: [True, False, ...] for 7 days (Mon-Sun)
    weekly_progress = models.JSONField(default=list)  # e.g. [true, true, false, ...]

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def reset_if_new_day(self):
        """Reset daily completion if it's a new day."""
        if self.last_checkin != date.today():
            self.is_done_today = False
            self.save()

# Note Model
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note {self.id}"

