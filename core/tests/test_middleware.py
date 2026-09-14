"""Tests for :class:`core.middleware.AyudaPYMiddleware`.

The middleware identifies anonymous visitors by a long-lived cookie, creating a
``Device`` and a ``User`` row the first time it sees one. It is deliberately
silent: no failure in here may break a request.
"""
from unittest import mock

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from core.middleware import DEVICE_ID_COOKIE_NAME, USER_TYPE_DEVICE, AyudaPYMiddleware
from core.models import Device, User

CHROME_UA = (
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/80.0.3987.132 Mobile Safari/537.36"
)


class MiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AyudaPYMiddleware(lambda request: HttpResponse("ok"))

    def get(self, path="/", **extra):
        request = self.factory.get(path, HTTP_USER_AGENT=CHROME_UA, **extra)
        return request, self.middleware(request)


class DeviceCreationTests(MiddlewareTestCase):
    def test_creates_a_device_for_a_first_time_visitor(self):
        request, _ = self.get()
        self.assertEqual(1, Device.objects.count())
        self.assertIsNotNone(request.ayuda_session["device"])

    def test_sets_the_device_cookie_on_the_response(self):
        request, response = self.get()
        self.assertIn(DEVICE_ID_COOKIE_NAME, response.cookies)
        self.assertEqual(
            request.ayuda_session["device"].device_id,
            response.cookies[DEVICE_ID_COOKIE_NAME].value,
        )

    def test_the_device_cookie_is_long_lived(self):
        _, response = self.get()
        self.assertIn("2067", response.cookies[DEVICE_ID_COOKIE_NAME]["expires"])

    def test_parses_the_user_agent_into_the_device(self):
        request, _ = self.get()
        device = request.ayuda_session["device"]
        self.assertEqual("Chrome Mobile", device.browser_family)
        self.assertEqual("80.0", device.browser_version)
        self.assertEqual("Android", device.os_family)
        self.assertEqual("10", device.os_version)
        self.assertEqual("Samsung", device.dev_brand)
        self.assertEqual(CHROME_UA, device.ua_string)

    def test_records_the_originating_ip_address(self):
        request = self.factory.get("/", HTTP_USER_AGENT=CHROME_UA, REMOTE_ADDR="190.128.1.1")
        self.middleware(request)
        self.assertEqual("190.128.1.1", request.ayuda_session["device"].created_ip_address)

    def test_devices_start_active(self):
        request, _ = self.get()
        self.assertEqual("ACTIVE", request.ayuda_session["device"].status)


class DeviceReuseTests(MiddlewareTestCase):
    def test_a_known_cookie_reuses_the_existing_device(self):
        first_request, first_response = self.get()
        device_id = first_response.cookies[DEVICE_ID_COOKIE_NAME].value

        second_request = self.factory.get("/", HTTP_USER_AGENT=CHROME_UA)
        second_request.COOKIES[DEVICE_ID_COOKIE_NAME] = device_id
        second_response = self.middleware(second_request)

        self.assertEqual(1, Device.objects.count())
        self.assertEqual(device_id, second_request.ayuda_session["device"].device_id)
        self.assertNotIn(DEVICE_ID_COOKIE_NAME, second_response.cookies)

    def test_an_unknown_cookie_creates_a_fresh_device(self):
        request = self.factory.get("/", HTTP_USER_AGENT=CHROME_UA)
        request.COOKIES[DEVICE_ID_COOKIE_NAME] = "00000000-0000-0000-0000-000000000000"
        response = self.middleware(request)

        self.assertEqual(1, Device.objects.count())
        self.assertNotEqual(
            "00000000-0000-0000-0000-000000000000",
            request.ayuda_session["device"].device_id,
        )
        self.assertIn(DEVICE_ID_COOKIE_NAME, response.cookies)


class UserCreationTests(MiddlewareTestCase):
    def test_creates_a_device_user_alongside_the_device(self):
        request, _ = self.get()
        user = request.ayuda_session["user"]

        self.assertEqual(1, User.objects.count())
        self.assertEqual(USER_TYPE_DEVICE, user.user_type)
        self.assertEqual(request.ayuda_session["device"].device_id, user.user_value)

    def test_a_returning_device_reuses_its_user(self):
        _, response = self.get()
        device_id = response.cookies[DEVICE_ID_COOKIE_NAME].value

        request = self.factory.get("/", HTTP_USER_AGENT=CHROME_UA)
        request.COOKIES[DEVICE_ID_COOKIE_NAME] = device_id
        self.middleware(request)

        self.assertEqual(1, User.objects.count())


class SilentFailureTests(MiddlewareTestCase):
    def test_a_request_without_a_user_agent_still_succeeds(self):
        request = self.factory.get("/")
        response = self.middleware(request)

        self.assertEqual(200, response.status_code)
        self.assertIsNone(request.ayuda_session["device"])
        self.assertIsNone(request.ayuda_session["user"])
        self.assertEqual(0, Device.objects.count())

    def test_a_database_error_does_not_break_the_response(self):
        with mock.patch.object(AyudaPYMiddleware, "do_create_device", side_effect=RuntimeError("boom")):
            request = self.factory.get("/", HTTP_USER_AGENT=CHROME_UA)
            response = self.middleware(request)

        self.assertEqual(200, response.status_code)
        self.assertIsNone(request.ayuda_session["device"])

    def test_ayuda_session_is_always_present(self):
        request = self.factory.get("/")
        self.middleware(request)
        self.assertEqual({"user", "device", "must_set_cookie"}, set(request.ayuda_session))


class GetVersionTests(MiddlewareTestCase):
    def test_joins_major_and_minor(self):
        self.assertEqual("80.0", self.middleware.get_version({"major": "80", "minor": "0"}))

    def test_major_only(self):
        self.assertEqual("80", self.middleware.get_version({"major": "80", "minor": None}))

    def test_unknown_version_is_empty(self):
        self.assertEqual("", self.middleware.get_version({"major": None, "minor": None}))
        self.assertEqual("", self.middleware.get_version({}))
