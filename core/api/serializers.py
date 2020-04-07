from rest_framework import serializers

from core.models import HelpRequest


# class HelpSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = HelpRequest
#         fields = ['title', 'message', 'name', 'phone']

class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpRequest
        fields = '__all__'