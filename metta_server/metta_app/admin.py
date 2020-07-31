from django.contrib import admin
from .models import Crop, SensorEntry, Schedule, TrayState

# Register your models here.
admin.site.register(Crop)
admin.site.register(SensorEntry)
admin.site.register(Schedule)
admin.site.register(TrayState)