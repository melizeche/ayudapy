from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from .models import HelpRequest


class HelpRequestSerializer(GeoModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ['id', 'title', 'message', 'name', 'phone', 'address', 'city', 'location', 'picture', 'active']
        geo_field = 'location'


class HelpRequestGeoJSONSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ['id', 'title', 'message', 'name']
        geo_field = 'location'