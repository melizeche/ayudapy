from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from ollas.models import OllaPopular


def unresolve(modeladmin, request, queryset):
    queryset.update(resolved=False)


def resolve(modeladmin, request, queryset):
    queryset.update(resolved=True)


def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)


def activate(modeladmin, request, queryset):
    queryset.update(active=True)

resolve.short_description = "Marcar ollas populares seleccionadas como resueltas"
unresolve.short_description = "Marcar ollas populares seleccionadas como NO resueltas"
deactivate.short_description = "Marcar ollas populares seleccionadas como inactivas"
activate.short_description = "Marcar ollas populares seleccionadas como activas"

# Register your models here.
class OllaPopularAdmin(LeafletGeoAdmin):
    list_display = (
        "__str__",
        "id",
        "name",
        "phone",
        "resolved",
        "active",
        "title",
        "message",
        "upvotes",
        "downvotes",
    )
    search_fields = ["title", "message", "name", "phone"]
    actions = [resolve, unresolve, deactivate, activate]

admin.site.register(OllaPopular, OllaPopularAdmin)