from django.urls import path

from core.api.views import list_pedidos

urlpatterns = [
    path('pedidos', list_pedidos)
]