from rest_framework import viewsets
from rest_framework import filters
from rest_framework_gis.filters import InBBoxFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models import HelpRequest
from core.serializers import HelpRequestSerializer, HelpRequestGeoJSONSerializer

"""
    API endpoints that allows search queries on HelpRequest 0
"""

# SEARCH HELP REQUESTS
class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])

class HelpRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HelpRequest.objects.filter(active=True).order_by('-id')
    serializer_class = HelpRequestSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, DynamicSearchFilter,]
    search_fields = ['title', 'phone',]
    filterset_fields = ['city']
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True


class HelpRequestGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HelpRequest.objects.filter(active=True).order_by('-pk')
    pagination_class = None
    serializer_class = HelpRequestGeoJSONSerializer
    bbox_filter_field = 'location'
    filter_backends = (InBBoxFilter, DynamicSearchFilter,)
    bbox_filter_include_overlapping = True

# DEVICES
