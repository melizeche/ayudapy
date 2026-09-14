from rest_framework import routers
from core import api as core_api
from org import api as org_api
from django.urls import include, path

PREFIX = "api/v1"

router = routers.DefaultRouter()
# CORE
router.register(r'helprequests', core_api.HelpRequestViewSet, 'helprequests')
router.register(r'helprequestsgeo', core_api.HelpRequestGeoViewSet, 'helprequestsgeo')
router.register(r'devices', core_api.DeviceViewSet, 'devices')
router.register(r'cities', core_api.CitiesViewSet, 'cities')
# ORG
router.register(r'donationcenters', org_api.DonationCenterViewSet, 'donationcenters')
router.register(r'donationcentersgeo', org_api.DonationCenterGeoViewSet, 'donationcentersgeo')

urlpatterns = [
    path(f"{PREFIX}/", include(router.urls)),
    path(f"{PREFIX}/stats-summary", core_api.StatsSummaryView),
    path(f"{PREFIX}/stats-daily", core_api.StatsDailyView)
]

