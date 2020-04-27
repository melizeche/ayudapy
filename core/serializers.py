from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from core.models import Device, HelpRequest


class HelpRequestSerializer(GeoModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ['id', 'title', 'message', 'name', 'phone', 'address', 'city', 'location', 'picture', 'active', 'added']
        geo_field = 'location'


class HelpRequestGeoJSONSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ['pk', 'title','name', 'added']
        geo_field = 'location'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = (
            'device_id',
            'ua_string',
            'status',
            'dev_brand',
            'dev_family',
            'dev_model',
            'os_family',
            'os_version',
            'browser_family',
            'browser_version'
        )


class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ['city', 'city_code']