from django.db import models

# Create your models here.
class Crop(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name