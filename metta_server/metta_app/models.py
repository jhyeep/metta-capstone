from django.db import models

# Create your models here.

class SensorEntry(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    sensor_id = models.TextField() #unused for now
    ec = models.TextField()
    temp = models.TextField()

class Schedule(models.Model):
    week = models.IntegerField()
    date = models.DateField()
    to_plant = models.TextField()
    to_transfer = models.TextField()
    to_harvest = models.TextField()

class TrayState(models.Model):
    date = models.DateField()
    tray1 = models.TextField()
    tray2 = models.TextField()
    tray3 = models.TextField()
    tray4 = models.TextField()