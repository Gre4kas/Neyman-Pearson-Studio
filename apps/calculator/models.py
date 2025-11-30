from django.db import models
from django.conf import settings

class CalculationHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Робимо ці поля необов'язковими, оскільки в матричному методі вони не використовуються так, як в статистичному
    alpha = models.FloatField(null=True, blank=True)
    h0_params = models.JSONField(null=True, blank=True)
    h1_params = models.JSONField(null=True, blank=True)
    
    # Тут зберігатимемо L* (граничне значення)
    threshold = models.FloatField(help_text="Граничне значення L*")
    
    # Тут зберігатимемо результат функції (значення неконтрольованого стану)
    power = models.FloatField(help_text="Мінімальне значення неконтрольованого стану")
    
    gamma = models.FloatField(null=True, blank=True, help_text="Randomization factor")
    
    # Тут зберігатимемо саму матрицю та вектор результатів (ймовірності стратегій)
    extra_data = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calculation for {self.user.username} at {self.created_at.strftime('%Y-%m-%d')}"