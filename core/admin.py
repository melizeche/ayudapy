from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import HelpRequest


def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)


def activate(modeladmin, request, queryset):
    queryset.update(active=True)


class HelpRequestAdmin(LeafletGeoAdmin):
    list_display = (
        "__str__",
        "id",
        "name",
        "phone",
        "active",
        "title",
        "message",
        "upvotes",
        "downvotes",
    )
    search_fields = ["title", "message", "name", "phone"]
    actions = [deactivate, activate]


deactivate.short_description = "Marcar pedidos seleccionados como inactivos"
activate.short_description = "Marcar pedidos seleccionados como activos"


admin.site.register(HelpRequest, HelpRequestAdmin)
