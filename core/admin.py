from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import HelpRequest

# Register your models here.
admin.site.register(HelpRequest, LeafletGeoAdmin)
