from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import HelpRequest


class HelpRequestAdmin(LeafletGeoAdmin):
    search_fields = ["title", "message", "name", "phone"]


admin.site.register(HelpRequest, HelpRequestAdmin)
