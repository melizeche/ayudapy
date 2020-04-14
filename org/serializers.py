from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from org.models import DonationCenter

class DonationCenterSerializer(GeoModelSerializer):
    class Meta:
        model = DonationCenter
        fields = ['id', 'name', 'phone',  'location', 'address', 'city', 'city_code', 'active', 'added']
        geo_field = 'location'

class DonationCenterGeoJSONSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = DonationCenter
        fields = ['pk', 'name', 'phone',  'location', 'address', 'city', 'city_code', 'active', 'added']
        geo_field = 'location'