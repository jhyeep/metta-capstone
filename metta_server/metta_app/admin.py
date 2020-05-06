from django.contrib import admin
from .models import Crop, SensorEntry

# Register your models here.
admin.site.register(Crop)
admin.site.register(SensorEntry)