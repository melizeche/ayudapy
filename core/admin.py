from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import (
    Category,
    HelpRequest,
    FrequentAskedQuestion,
)


def unresolve(modeladmin, request, queryset):
    queryset.update(resolved=False)


def resolve(modeladmin, request, queryset):
    queryset.update(resolved=True)


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
        "resolved",
        "active",
        "title",
        "message",
        "upvotes",
        "downvotes",
    )
    search_fields = ["title", "message", "name", "phone"]
    actions = [resolve, unresolve, deactivate, activate]


resolve.short_description = "Marcar pedidos seleccionados como resueltos"
unresolve.short_description = "Marcar pedidos seleccionados como NO resueltos"
deactivate.short_description = "Marcar pedidos seleccionados como inactivos"
activate.short_description = "Marcar pedidos seleccionados como activos"


admin.site.register(HelpRequest, HelpRequestAdmin)


class FrequentAskedQuestionAdmin(admin.ModelAdmin):
    """
    Customize admin's FAQ change list page for easier management
    """
    list_display = ('question', 'order', 'active')
    search_fields = ['question']
    list_filter = ['active']


# FAQ model registration & applied customization
admin.site.register(FrequentAskedQuestion, FrequentAskedQuestionAdmin)
admin.site.register(Category)
