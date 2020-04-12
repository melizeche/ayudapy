from django.http import Http404
from rest_framework import viewsets, status, mixins
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.filters import InBBoxFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models import HelpRequest, Device
from core.serializers import HelpRequestSerializer, HelpRequestGeoJSONSerializer, DeviceSerializer

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

"""
API to create/update/remove devices.
Will be used by the Mobile Client
"""


class DeviceViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = DeviceSerializer
    queryset = Device.objects.all()
    lookup_field = "device_id"

