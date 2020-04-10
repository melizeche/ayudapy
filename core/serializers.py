from rest_framework import serializers

from .models import HelpRequest


class HelpRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HelpRequest
        fields = ['id', 'title', 'message', 'name', 'phone', 'address', 'city', 'location', 'picture', 'active']