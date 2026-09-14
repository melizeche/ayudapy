"""Tests for the ``core`` REST API (``/api/v1/``).

These endpoints back the iOS and Android clients, so the shape of the responses
matters as much as their contents.
"""
import json
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Device, HelpRequest, User
from core.tests.helpers import ASUNCION, ENCARNACION, GeocodedTestCase, make_help_request

HELP_REQUESTS_URL = "/api/v1/helprequests/"
GEO_URL = "/api/v1/helprequestsgeo/"
CITIES_URL = "/api/v1/cities/"
DEVICES_URL = "/api/v1/devices/"
STATS_SUMMARY_URL = "/api/v1/stats-summary"
STATS_DAILY_URL = "/api/v1/stats-daily"

# A bounding box (min lon, min lat, max lon, max lat) around Asunción.
ASUNCION_BBOX = "-57.7,-25.4,-57.4,-25.1"


def days_ago(days):
    """An aware datetime, for back-dating the auto_now_add ``added`` column."""
    return timezone.now() - timedelta(days=days)


class HelpRequestApiTests(GeocodedTestCase):
    def test_lists_open_requests(self):
        help_request = make_help_request(title="Necesito comida")

        response = self.client.get(HELP_REQUESTS_URL)

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual(1, body["count"])
        self.assertEqual(help_request.pk, body["results"][0]["id"])

    def test_serialises_the_documented_fields(self):
        make_help_request()
        result = self.client.get(HELP_REQUESTS_URL).json()["results"][0]
        self.assertEqual(
            {"id", "title", "message", "name", "phone", "address", "city", "location", "picture", "active", "added"},
            set(result),
        )

    def test_hides_inactive_requests(self):
        inactive = make_help_request()
        HelpRequest.objects.filter(pk=inactive.pk).update(active=False)
        self.assertEqual(0, self.client.get(HELP_REQUESTS_URL).json()["count"])

    def test_hides_resolved_requests(self):
        resolved = make_help_request()
        HelpRequest.objects.filter(pk=resolved.pk).update(resolved=True)
        self.assertEqual(0, self.client.get(HELP_REQUESTS_URL).json()["count"])

    def test_newest_requests_come_first(self):
        older = make_help_request()
        newer = make_help_request()
        results = self.client.get(HELP_REQUESTS_URL).json()["results"]
        self.assertEqual([newer.pk, older.pk], [r["id"] for r in results])

    def test_pages_at_twenty_five_results(self):
        for _ in range(26):
            make_help_request()
        body = self.client.get(HELP_REQUESTS_URL).json()
        self.assertEqual(26, body["count"])
        self.assertEqual(25, len(body["results"]))
        self.assertIsNotNone(body["next"])

    def test_a_single_request_can_be_retrieved(self):
        help_request = make_help_request(title="Necesito comida")
        response = self.client.get(f"{HELP_REQUESTS_URL}{help_request.pk}/")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Necesito comida", response.json()["title"])


class HelpRequestApiFilterTests(GeocodedTestCase):
    def test_filters_by_city(self):
        wanted = make_help_request()
        self.use_geocoder({"city": "Luque"})
        make_help_request()

        body = self.client.get(HELP_REQUESTS_URL, {"city": "Asunción"}).json()

        self.assertEqual([wanted.pk], [r["id"] for r in body["results"]])

    def test_filters_by_bounding_box(self):
        inside = make_help_request(location=ASUNCION)
        make_help_request(location=ENCARNACION)

        body = self.client.get(HELP_REQUESTS_URL, {"in_bbox": ASUNCION_BBOX}).json()

        self.assertEqual([inside.pk], [r["id"] for r in body["results"]])

    def test_filters_by_exact_date(self):
        today = make_help_request()
        yesterday = make_help_request()
        HelpRequest.objects.filter(pk=yesterday.pk).update(added=days_ago(1))

        body = self.client.get(HELP_REQUESTS_URL, {"added__date": date.today().isoformat()}).json()

        self.assertEqual([today.pk], [r["id"] for r in body["results"]])

    def test_filters_by_date_range(self):
        old = make_help_request()
        recent = make_help_request()
        HelpRequest.objects.filter(pk=old.pk).update(added=days_ago(10))

        body = self.client.get(
            HELP_REQUESTS_URL,
            {"added__gte": (date.today() - timedelta(days=1)).isoformat()},
        ).json()

        self.assertEqual([recent.pk], [r["id"] for r in body["results"]])

    def test_searches_the_fields_named_in_the_query_string(self):
        wanted = make_help_request(title="Necesito comida")
        make_help_request(title="Necesito frazadas")

        body = self.client.get(
            HELP_REQUESTS_URL, {"search": "comida", "search_fields": "title"}
        ).json()

        self.assertEqual([wanted.pk], [r["id"] for r in body["results"]])

    def test_search_without_search_fields_matches_nothing_specific(self):
        make_help_request(title="Necesito comida")
        # DynamicSearchFilter only searches the fields the caller asks for.
        body = self.client.get(HELP_REQUESTS_URL, {"search": "comida"}).json()
        self.assertEqual(1, body["count"])

    def test_searches_by_phone_number(self):
        wanted = make_help_request(phone="0981555111")
        make_help_request(phone="0982555222")

        body = self.client.get(
            HELP_REQUESTS_URL, {"search": "0981555111", "search_fields": "phone"}
        ).json()

        self.assertEqual([wanted.pk], [r["id"] for r in body["results"]])


class HelpRequestGeoApiTests(GeocodedTestCase):
    def test_returns_a_geojson_feature_collection(self):
        help_request = make_help_request(title="Necesito comida")

        body = self.client.get(GEO_URL).json()

        self.assertEqual("FeatureCollection", body["type"])
        feature = body["features"][0]
        self.assertEqual("Feature", feature["type"])
        self.assertEqual("Point", feature["geometry"]["type"])
        self.assertEqual(
            [help_request.location.x, help_request.location.y],
            feature["geometry"]["coordinates"],
        )
        # ``pk`` is declared as a regular field, so it rides along in
        # ``properties`` rather than becoming the GeoJSON feature id.
        self.assertEqual({"pk", "title", "name", "added"}, set(feature["properties"]))
        self.assertEqual(help_request.pk, feature["properties"]["pk"])

    def test_is_not_paginated(self):
        for _ in range(26):
            make_help_request()
        body = self.client.get(GEO_URL).json()
        self.assertEqual(26, len(body["features"]))

    def test_hides_inactive_requests(self):
        inactive = make_help_request()
        HelpRequest.objects.filter(pk=inactive.pk).update(active=False)
        self.assertEqual([], self.client.get(GEO_URL).json()["features"])

    def test_filters_by_bounding_box(self):
        inside = make_help_request(location=ASUNCION)
        make_help_request(location=ENCARNACION)

        body = self.client.get(GEO_URL, {"in_bbox": ASUNCION_BBOX}).json()

        self.assertEqual([inside.pk], [f["properties"]["pk"] for f in body["features"]])

    def test_is_read_only(self):
        response = self.client.post(GEO_URL, {})
        self.assertEqual(405, response.status_code)


class CitiesApiTests(GeocodedTestCase):
    def test_lists_each_city_once(self):
        make_help_request()
        make_help_request()
        self.use_geocoder({"city": "Luque"})
        make_help_request()

        body = self.client.get(CITIES_URL).json()

        self.assertEqual(
            [{"city": "Asunción", "city_code": "Asuncion"}, {"city": "Luque", "city_code": "Luque"}],
            sorted(body, key=lambda row: row["city_code"]),
        )

    def test_is_empty_when_there_are_no_requests(self):
        self.assertEqual([], self.client.get(CITIES_URL).json())


class StatsSummaryApiTests(GeocodedTestCase):
    def test_counts_open_resolved_and_recent_requests(self):
        make_help_request(phone="0981111111")
        make_help_request(phone="0982222222")
        resolved = make_help_request(phone="0983333333")
        HelpRequest.objects.filter(pk=resolved.pk).update(resolved=True)

        body = self.client.get(STATS_SUMMARY_URL).json()

        self.assertEqual(2, body["total_active"])
        self.assertEqual(2, body["total_active_unique_phone"])
        self.assertEqual(1, body["total_resolved"])
        self.assertEqual(3, body["today"])
        self.assertEqual(0, body["yesterday"])

    def test_counts_yesterdays_requests_separately(self):
        yesterday = make_help_request()
        HelpRequest.objects.filter(pk=yesterday.pk).update(added=days_ago(1))

        body = self.client.get(STATS_SUMMARY_URL).json()

        self.assertEqual(0, body["today"])
        self.assertEqual(1, body["yesterday"])

    def test_is_all_zeroes_on_an_empty_database(self):
        body = self.client.get(STATS_SUMMARY_URL).json()
        self.assertEqual({0}, set(body.values()))


class StatsDailyApiTests(GeocodedTestCase):
    def test_requires_a_date_range(self):
        response = self.client.get(STATS_DAILY_URL)
        self.assertEqual(400, response.status_code)
        self.assertIn("date_from", response.json()["msg"])

    def test_groups_open_requests_by_day(self):
        make_help_request(phone="0981111111")
        make_help_request(phone="0982222222")

        body = self.client.get(
            STATS_DAILY_URL,
            {"date_from": (date.today() - timedelta(days=1)).isoformat(),
             "date_to": (date.today() + timedelta(days=1)).isoformat()},
        ).json()

        self.assertEqual([{"date": date.today().isoformat(), "total": 2}], body["total_active"])

    def test_counts_each_phone_number_once(self):
        make_help_request(phone="0981111111")
        make_help_request(phone="0981111111")

        body = self.client.get(
            STATS_DAILY_URL,
            {"date_from": (date.today() - timedelta(days=1)).isoformat(),
             "date_to": (date.today() + timedelta(days=1)).isoformat()},
        ).json()

        self.assertEqual([{"date": date.today().isoformat(), "total": 1}], body["total_active_unique_phone"])

    def test_reports_an_empty_range(self):
        make_help_request()
        body = self.client.get(
            STATS_DAILY_URL,
            {"date_from": "2019-01-01", "date_to": "2019-12-31"},
        ).json()
        self.assertEqual({"total_active": [], "total_active_unique_phone": [], "total_resolved": []}, body)


class DeviceApiTests(TestCase):
    """The mobile clients register themselves through ``/api/v1/devices/``."""

    payload = {
        "device_id": "11111111-2222-3333-4444-555555555555",
        "ua_string": "AyudaPY/1.0 iOS",
        "os_family": "iOS",
        "os_version": "13.4",
    }

    def test_registering_a_device_creates_it(self):
        response = self.client.post(DEVICES_URL, self.payload, content_type="application/json")

        self.assertEqual(201, response.status_code)
        device = Device.objects.get()
        self.assertEqual(self.payload["device_id"], device.device_id)
        self.assertEqual("iOS", device.os_family)

    def test_registering_a_device_creates_its_user(self):
        self.client.post(DEVICES_URL, self.payload, content_type="application/json")

        user = User.objects.get()
        self.assertEqual("DEVICE_USER", user.user_type)
        self.assertEqual(self.payload["device_id"], user.user_value)

    def test_device_id_is_required(self):
        response = self.client.post(DEVICES_URL, {"ua_string": "x"}, content_type="application/json")
        self.assertEqual(400, response.status_code)
        self.assertIn("device_id", response.json())

    def test_device_ids_are_unique(self):
        self.client.post(DEVICES_URL, self.payload, content_type="application/json")
        response = self.client.post(DEVICES_URL, self.payload, content_type="application/json")
        self.assertEqual(400, response.status_code)

    def test_a_device_is_looked_up_by_its_device_id(self):
        self.client.post(DEVICES_URL, self.payload, content_type="application/json")
        response = self.client.get(f"{DEVICES_URL}{self.payload['device_id']}/")
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.payload["device_id"], response.json()["device_id"])

    def test_a_device_can_update_its_push_token(self):
        self.client.post(DEVICES_URL, self.payload, content_type="application/json")
        response = self.client.patch(
            f"{DEVICES_URL}{self.payload['device_id']}/",
            {"ua_string": "AyudaPY/1.1 iOS"},
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("AyudaPY/1.1 iOS", Device.objects.get().ua_string)

    def test_a_device_can_be_deleted(self):
        self.client.post(DEVICES_URL, self.payload, content_type="application/json")
        response = self.client.delete(f"{DEVICES_URL}{self.payload['device_id']}/")
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, Device.objects.count())

    def test_devices_are_not_listable(self):
        # The viewset deliberately omits ListModelMixin: devices are private.
        response = self.client.get(DEVICES_URL)
        self.assertEqual(405, response.status_code)
