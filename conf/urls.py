"""ayudapy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from core import views as core_views
from core import api as core_api

router = routers.DefaultRouter()
router.register(r'helprequests', core_api.HelpRequestViewSet)
router.register(r'helprequestsgeo', core_api.HelpRequestGeoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('', core_views.home, name='home'),
    path('recibir', TemplateView.as_view(template_name="info_request.html")),
    path('solicitar', core_views.request_form, name="request-form"),
    path('dar', TemplateView.as_view(template_name="info_give.html")),
    path('legal', TemplateView.as_view(template_name="legal.html")),
    path('pedidos/<int:id>', core_views.view_request, name='pedidos-detail'),
    path('pedidos_ciudad/<slug:city>', core_views.list_by_city, name='pedidos-by-city'),
    path('pedidos', core_views.list_requests),
    path('preguntas_frecuentes', core_views.view_faq, name='general_faq'),
    path('contacto', TemplateView.as_view(template_name="contact_us.html"), name='contact_us')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
