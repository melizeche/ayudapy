from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import HelpRequest, FrequentAskedQuestion

# Register your models here.
admin.site.register(HelpRequest, LeafletGeoAdmin)


class FrequentAskedQuestionAdmin(admin.ModelAdmin):
    """
    Customize admin's FAQ change list page for easier management
    """
    list_display = ('question', 'order', 'active')
    search_fields = ['question']
    list_filter = ['active']

# FAQ model registration & applied customization
admin.site.register(FrequentAskedQuestion, FrequentAskedQuestionAdmin)