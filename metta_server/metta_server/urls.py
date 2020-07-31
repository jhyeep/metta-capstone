"""metta_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
import metta_app.views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('metta_app.urls')),
    path('app/latest_sensor_val', main_views.latest_sensor_val, name="latest_sensor_val"),
    path('app/scheduler', main_views.scheduler, name="scheduler"),
    path('app/tray_state', main_views.tray_state, name="tray_state"),
    path('new', main_views.sensorentry_new, name="sensorentry_new"),
    path('raw_data', main_views.raw_data, name="raw_data"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
