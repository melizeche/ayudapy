from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from ollas.models import OllaPopular


class OllaPopularSerializer(GeoModelSerializer):
    class Meta:
        model = OllaPopular
        fields = ['id', 'title', 'message', 'name', 'phone', 'address', 'city', 'location', 'picture', 'active', 'added']
        geo_field = 'location'


class OllaPopularGeoJSONSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = OllaPopular
        fields = ['pk', 'title','name', 'added']
        geo_field = 'location'
