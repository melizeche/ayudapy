from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import DonationCenter, Organization, Profile


def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)


def activate(modeladmin, request, queryset):
    queryset.update(active=True)


deactivate.short_description = "Marcar seleccionados como inactivos"
activate.short_description = "Marcar seleccionados como activos"


class DonationCenterAdmin(LeafletGeoAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "active",
        "city",
    )
    search_fields = ["name", "city", "phone"]
    actions = [deactivate, activate]


class ProfileAdmin(LeafletGeoAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "active",
        "city",
    )
    search_fields = ["name", "city", "phone"]
    actions = [deactivate, activate]


admin.site.register(DonationCenter, DonationCenterAdmin)
admin.site.register(Organization)
admin.site.register(Profile, ProfileAdmin)
