from rest_framework import routers
from core import api as core_api
from django.urls import include, path

PREFIX = "api/v1"

router = routers.DefaultRouter()
router.register(r'helprequests', core_api.HelpRequestViewSet)
router.register(r'helprequestsgeo', core_api.HelpRequestGeoViewSet)
router.register(r'devices', core_api.DeviceViewSet)

urlpatterns = [
    path(f"{PREFIX}/", include(router.urls)),
]

