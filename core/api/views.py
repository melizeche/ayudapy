from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.api.serializers import HelpSerializer
from core.models import HelpRequest

@api_view()
def list_pedidos(request):
    pedidos = HelpRequest.objects.filter(active=True)
    serializer = HelpSerializer(pedidos, many=True)
    return Response(serializer.data)