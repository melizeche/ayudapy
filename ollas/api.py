from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from core.middleware import USER_TYPE_DEVICE
from core.serializers import DeviceSerializer
from core.models import Device, User

from ollas.models import OllaPopular
from ollas.serializers import OllaPopularSerializer, OllaPopularGeoJSONSerializer

"""
    API endpoints that allows search queries on OllaPopular 0
"""


# SEARCH OLLAS POPULARES
class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])


class OllaPopularViewSet(viewsets.ModelViewSet):
    queryset = OllaPopular.objects.filter(active=True, resolved=False).order_by('-id')
    serializer_class = OllaPopularSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, DynamicSearchFilter, ]
    search_fields = ['title', 'phone',]
    filterset_fields = {
            'added': ['gte', 'lte'],
            'city': ['exact'],
    }
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True


class OllaPopularGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OllaPopular.objects.filter(active=True, resolved=False).order_by('-pk')
    pagination_class = None
    serializer_class = OllaPopularGeoJSONSerializer
    bbox_filter_field = 'location'
    filter_backends = (InBBoxFilter, DynamicSearchFilter,)
    bbox_filter_include_overlapping = True
