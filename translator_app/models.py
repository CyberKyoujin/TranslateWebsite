from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Translation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.CharField(max_length=100, default='Не указан')
    text = models.TextField(max_length=10000)
    translation = models.TextField(max_length=10000)
    date = models.DateTimeField(default=timezone.now())
    
class Wordbook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.CharField(max_length=100, default='Нет названия')
    phrase = models.TextField(max_length=200)
    translated = models.TextField(max_length=400)
    date = models.DateTimeField(default=timezone.now())
    
    