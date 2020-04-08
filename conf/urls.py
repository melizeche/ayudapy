"""ayudapy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView


from core import views as core_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('recibir', TemplateView.as_view(template_name="info_request.html")),
    path('solicitar', core_views.request_form, name="request-form"),
    path('dar', TemplateView.as_view(template_name="info_give.html")),
    path('legal', TemplateView.as_view(template_name="legal.html")),
    path('pedidos/<int:id>', core_views.view_request, name='pedidos-detail'),
    path('pedidos', core_views.list_requests),
    path('api/', include(('core.api.urls', 'pedidos'), namespace='pedidos')),
    path('pedidos_ciudad/<slug:city>', core_views.list_by_city, name='pedidos-by-city'),
    path('pedidos', core_views.list_requests)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
