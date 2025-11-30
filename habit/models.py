from django.db import models
from django.utils import timezone

# Create your models here.

class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['habit', 'date']  
    
    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.habit.name} - {self.date} - {status}"