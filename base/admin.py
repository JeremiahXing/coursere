from django.contrib import admin
from . import models

admin.site.site_header = 'Coursere admin panel'

admin.site.register(models.Topic)
admin.site.register(models.Room)
admin.site.register(models.Profile)