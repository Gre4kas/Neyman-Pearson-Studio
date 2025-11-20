from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField  # или models.JSONField в Django 3.1+

class CalculationHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    alpha = models.FloatField(null=True, blank=True)
    # Store input parameters as JSON
    h0_params = models.JSONField()
    h1_params = models.JSONField()
    # Store results
    threshold = models.FloatField()
    power = models.FloatField()
    gamma = models.FloatField(null=True, blank=True, help_text="Randomization factor")    
    extra_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calculation for {self.user.username} at {self.created_at.strftime('%Y-%m-%d')}"