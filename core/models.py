from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Offer(models.Model):
    name = models.CharField(max_length=150)
    value_props = models.JSONField()
    ideal_use_cases = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name}'
    
class Lead(models.Model):
    intent_choices = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='leads')
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    industry = models.CharField(max_length=180)
    location = models.CharField(max_length=180, null=True, blank=True)
    linkedin_bio = models.CharField(max_length=360, null=True, blank=True)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    intent_label = models.CharField(choices=intent_choices, max_length=10, null=True)
    reasoning = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.role} - {self.company}'