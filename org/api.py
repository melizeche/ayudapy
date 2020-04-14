from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from org.models import DonationCenter
from org.serializers import DonationCenterSerializer, DonationCenterGeoJSONSerializer

"""
    API endpoints that allows search queries on DonationCenter
"""


# SEARCH DonationCenter
class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])


class DonationCenterViewSet(viewsets.ModelViewSet):
    queryset = DonationCenter.objects.filter(active=True).order_by('-id')
    serializer_class = DonationCenterSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, DynamicSearchFilter,]
    search_fields = ['title', 'phone',]
    filterset_fields = ['city']
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True


class DonationCenterGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DonationCenter.objects.filter(active=True).order_by('-pk')
    pagination_class = None
    serializer_class = DonationCenterGeoJSONSerializer
    bbox_filter_field = 'location'
    filter_backends = (InBBoxFilter, DynamicSearchFilter,)
    bbox_filter_include_overlapping = True