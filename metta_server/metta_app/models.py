from django.db import models

# Create your models here.
class Crop(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name

class SensorEntry(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    sensor_id = models.TextField()
    # data = models.TextField()
    ec = models.TextField()
    temp = models.TextField()