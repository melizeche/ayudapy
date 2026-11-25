from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import DonationCenter, Organization, Profile, Pool


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
    search_fields = ["=id", "name", "city", "phone"]
    actions = [deactivate, activate]


class ProfileAdmin(LeafletGeoAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "active",
        "city",
    )
    search_fields = ["=id", "name", "city", "phone"]
    actions = [deactivate, activate]


class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ["=id", "name"]


class PoolAdmin(LeafletGeoAdmin):
    search_fields = ["=id", "name"]


admin.site.register(DonationCenter, DonationCenterAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Pool, PoolAdmin)
