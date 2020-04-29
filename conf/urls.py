"""ayudapy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from conf import api_urls
from core import views as core_views
from org import views as org_views
from org.views import RestrictedView

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('jara/', admin.site.urls),
    # home
    path('', core_views.home, name='home'),
    path('dar', TemplateView.as_view(template_name="giver/info.html")),
    path('legal', TemplateView.as_view(template_name="footer/legal.html"), name='legal'),
    path('voluntario/legal', TemplateView.as_view(template_name="volunteer/info.html"), name='voluntariolegal'),
    path('preguntas_frecuentes', core_views.view_faq, name='general_faq'),
    path('contacto', TemplateView.as_view(template_name="footer/contact_us.html"), name='contact_us'),
    # help requests
    path('recibir', TemplateView.as_view(template_name="help_request/info.html")),
    path('solicitar', core_views.request_form, name="request-form"),
    path('pedidos/<int:id>', core_views.view_request, name='pedidos-detail'),
    path('pedidos_ciudad/<slug:city>', core_views.list_by_city, name='pedidos-by-city'),
    path('pedidos', core_views.list_requests),
    # donations
    path('ceder', org_views.donation_form, name="donation-form"),
    path('donar', RestrictedView.as_view()),
    path('donaciones', org_views.list_donation),
    path('donaciones_ciudad/<slug:city>', org_views.list_donation_by_city, name='donation-by-city'),
    path('donaciones/<int:id>', org_views.view_donation_center, name='donaciones-detail'),
    # volunteer
    path('voluntario', TemplateView.as_view(template_name="volunteer/form.html"), name='voluntario'),
    # stats
    path('stats', core_views.stats, name='stats'),
    # login/logout
    path('accounts/', include('django.contrib.auth.urls')),
]
urlpatterns += api_urls.urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
