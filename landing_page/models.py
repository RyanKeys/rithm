from django.db import models
from datetime import datetime

# Create your models here.


class Game(models.Model):
    name = models.CharField("Game Name", max_length=120)
    publisher = models.CharField(max_length=60)
    publish_date = models.DateTimeField("Event Date")
    link = models.URLField(blank=True)
    description = models.TextField(blank=True)
