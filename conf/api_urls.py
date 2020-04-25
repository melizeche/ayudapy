from rest_framework import routers
from core import api as core_api
from org import api as org_api
from ollas import api as ollas_api
from django.urls import include, path

PREFIX = "api/v1"

router = routers.DefaultRouter()
# CORE
router.register(r'helprequests', core_api.HelpRequestViewSet, 'helprequests')
router.register(r'helprequestsgeo', core_api.HelpRequestGeoViewSet)
router.register(r'devices', core_api.DeviceViewSet)
# ORG
router.register(r'donationcenters', org_api.DonationCenterViewSet)
router.register(r'donationcentersgeo', org_api.DonationCenterGeoViewSet)
# Ollas Populares
router.register(r'ollaspopulares', ollas_api.OllaPopularViewSet, 'ollaspopulares')
router.register(r'ollaspopularesgeo', ollas_api.OllaPopularGeoViewSet)

urlpatterns = [
    path(f"{PREFIX}/", include(router.urls)),
]

