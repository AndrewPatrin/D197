from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    STATUS = (
        ('common', 'common'),
        ('admin', 'admin')
    )
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS, default='common')

    def __str__(self):
        return f'{self.username}'