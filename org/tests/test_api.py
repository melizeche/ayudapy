"""Tests for the ``org`` REST API (``/api/v1/donationcenters*``)."""
from django.test import TestCase

from core.tests.helpers import ASUNCION, ENCARNACION
from org.models import DonationCenter
from org.tests.test_views import make_donation_center

CENTERS_URL = "/api/v1/donationcenters/"
CENTERS_GEO_URL = "/api/v1/donationcentersgeo/"
ASUNCION_BBOX = "-57.7,-25.4,-57.4,-25.1"


class DonationCenterApiTests(TestCase):
    def test_lists_active_centers(self):
        center = make_donation_center(name="Centro de acopio")

        response = self.client.get(CENTERS_URL)

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual(1, body["count"])
        self.assertEqual(center.pk, body["results"][0]["id"])

    def test_serialises_the_documented_fields(self):
        make_donation_center()
        result = self.client.get(CENTERS_URL).json()["results"][0]
        self.assertEqual(
            {"id", "name", "phone", "location", "address", "city", "city_code", "active", "added"},
            set(result),
        )

    def test_hides_inactive_centers(self):
        center = make_donation_center()
        DonationCenter.objects.filter(pk=center.pk).update(active=False)
        self.assertEqual(0, self.client.get(CENTERS_URL).json()["count"])

    def test_newest_centers_come_first(self):
        older = make_donation_center()
        newer = make_donation_center()
        results = self.client.get(CENTERS_URL).json()["results"]
        self.assertEqual([newer.pk, older.pk], [c["id"] for c in results])

    def test_pages_at_twenty_five_results(self):
        for index in range(26):
            make_donation_center(name=f"Centro {index}")
        body = self.client.get(CENTERS_URL).json()
        self.assertEqual(26, body["count"])
        self.assertEqual(25, len(body["results"]))

    def test_a_single_center_can_be_retrieved(self):
        center = make_donation_center(name="Centro de acopio")
        response = self.client.get(f"{CENTERS_URL}{center.pk}/")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Centro de acopio", response.json()["name"])

    def test_filters_by_city(self):
        wanted = make_donation_center(city="Asunción")
        make_donation_center(city="Luque")

        body = self.client.get(CENTERS_URL, {"city": "Asunción"}).json()

        self.assertEqual([wanted.pk], [c["id"] for c in body["results"]])

    def test_filters_by_bounding_box(self):
        inside = make_donation_center(location=ASUNCION)
        make_donation_center(location=ENCARNACION)

        body = self.client.get(CENTERS_URL, {"in_bbox": ASUNCION_BBOX}).json()

        self.assertEqual([inside.pk], [c["id"] for c in body["results"]])

    def test_searches_the_fields_named_in_the_query_string(self):
        wanted = make_donation_center(phone="0981555111")
        make_donation_center(phone="0982555222")

        body = self.client.get(
            CENTERS_URL, {"search": "0981555111", "search_fields": "phone"}
        ).json()

        self.assertEqual([wanted.pk], [c["id"] for c in body["results"]])


class DonationCenterGeoApiTests(TestCase):
    def test_returns_a_geojson_feature_collection(self):
        center = make_donation_center(name="Centro de acopio")

        body = self.client.get(CENTERS_GEO_URL).json()

        self.assertEqual("FeatureCollection", body["type"])
        feature = body["features"][0]
        self.assertEqual("Point", feature["geometry"]["type"])
        self.assertEqual(
            [center.location.x, center.location.y], feature["geometry"]["coordinates"]
        )
        self.assertEqual("Centro de acopio", feature["properties"]["name"])
        self.assertEqual(center.pk, feature["properties"]["pk"])

    def test_is_not_paginated(self):
        for index in range(26):
            make_donation_center(name=f"Centro {index}")
        self.assertEqual(26, len(self.client.get(CENTERS_GEO_URL).json()["features"]))

    def test_hides_inactive_centers(self):
        center = make_donation_center()
        DonationCenter.objects.filter(pk=center.pk).update(active=False)
        self.assertEqual([], self.client.get(CENTERS_GEO_URL).json()["features"])

    def test_filters_by_bounding_box(self):
        inside = make_donation_center(location=ASUNCION)
        make_donation_center(location=ENCARNACION)

        body = self.client.get(CENTERS_GEO_URL, {"in_bbox": ASUNCION_BBOX}).json()

        self.assertEqual([inside.pk], [f["properties"]["pk"] for f in body["features"]])

    def test_is_read_only(self):
        self.assertEqual(405, self.client.post(CENTERS_GEO_URL, {}).status_code)
