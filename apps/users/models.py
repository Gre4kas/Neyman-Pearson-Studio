from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Make email unique and required
    email = models.EmailField('Email адрес', unique=True)
    
    # Require email field
    REQUIRED_FIELDS = ['email']