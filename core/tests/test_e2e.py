"""End-to-end tests: a real browser uses the site the way a person does.

They catch failures that only happen in the browser, such as JavaScript errors
or a third-party script that no longer loads. Example: the markercluster 404
left /pedidos without markers while every API response was correct.

The tests need Playwright and Chromium::

    pip install -r requirements-dev.txt
    playwright install --with-deps chromium

Without Playwright they are skipped. To run only these tests::

    python manage.py test --tag=e2e

To run everything else::

    python manage.py test --exclude-tag=e2e
"""
import os
import re
from unittest import skipUnless

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import connections
from django.test import override_settings, tag

from core.models import HelpRequest
from core.tests.helpers import mock_geocoder
from org.tests.test_views import make_donation_center

try:
    from playwright.sync_api import expect, sync_playwright
except ImportError:  # pragma: no cover - depends on the environment
    sync_playwright = None

# A transparent 1x1 PNG, served instead of OpenStreetMap tiles.
BLANK_TILE = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000105fe02fea70000000049454e44ae426082"
)


@tag("e2e")
@skipUnless(sync_playwright, "Playwright is not installed (see requirements-dev.txt)")
# The live server serves the source files instead of the minified bundles
# that only exist after collectstatic. The JavaScript is the same.
@override_settings(PIPELINE={**settings.PIPELINE, "PIPELINE_ENABLED": False})
class HelpRequestJourneyTests(StaticLiveServerTestCase):
    # TransactionTestCase empties the database after each test. This restores
    # the data from migrations, such as the categories, for the tests that run next.
    serialized_rollback = True

    @classmethod
    def setUpClass(cls):
        # Playwright's sync API runs an event loop on this thread, so Django
        # would otherwise refuse database access from the test.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        # Starting Playwright changes the async context, so Django hands out new
        # connection objects afterwards. Django stores its copy of the migration
        # data (for serialized_rollback) on the old ones, so move it across.
        serialized = {
            alias: connections[alias]._test_serialized_contents
            for alias in connections
            if hasattr(connections[alias], "_test_serialized_contents")
        }
        cls.playwright = sync_playwright().start()
        for alias, contents in serialized.items():
            connections[alias]._test_serialized_contents = contents
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()
        os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)

    def setUp(self):
        super().setUp()
        # The live server runs in a thread of this process, so this patch also
        # stops it from calling Nominatim when the form saves.
        geocoder = mock_geocoder({"city": "Asunción"})
        geocoder.__enter__()
        self.addCleanup(geocoder.__exit__, None, None, None)

        self.context = self.browser.new_context(locale="es-PY", viewport={"width": 1280, "height": 900})
        self.addCleanup(self.context.close)
        # CDN scripts load for real: catching a broken one is part of the point.
        # Map tiles and analytics do not matter to the test, so they are stubbed.
        self.context.route(
            re.compile(r"https://([a-z]\.)?tile\.openstreetmap\.org/.*"),
            lambda route: route.fulfill(body=BLANK_TILE, content_type="image/png"),
        )
        self.context.route(re.compile(r"https://www\.(googletagmanager|google-analytics)\.com/.*"), lambda r: r.abort())

        self.page = self.context.new_page()
        self.page.set_default_timeout(15_000)
        self.js_errors = []
        self.page.on("pageerror", lambda error: self.js_errors.append(str(error)))

    def url(self, path):
        return f"{self.live_server_url}{path}"

    def assertNoJavaScriptErrors(self):
        self.assertEqual([], self.js_errors, "the page raised JavaScript errors")

    def fill_request_form(self, title):
        page = self.page
        page.goto(self.url("/solicitar"))
        page.fill("#id_title", title)
        page.fill("#id_message", "Somos 5 en casa y necesitamos alimentos no perecederos.")
        page.click("label[for=viveres]")
        page.fill("#id_name", "María Prueba")
        page.fill("#id_phone", "0981555123")
        page.fill("#id_address", "Calle Palma 123")

        # Mark the location as the help text says: pick the marker tool, then
        # click the map. The map opens on LEAFLET_CONFIG's DEFAULT_CENTER, which
        # is also where /pedidos opens, so the new request shows up there.
        page.click(".leaflet-draw-draw-marker")
        page.locator(".leaflet-container").first.click()
        expect(page.locator("#id_location")).to_have_value(re.compile(r'"type":\s*"Point"'))

    def test_a_new_request_appears_on_the_map_and_in_the_list(self):
        title = "Necesito víveres para mi familia"
        self.fill_request_form(title)
        self.page.click("#submit")
        self.page.wait_for_load_state()

        # The form redirects to the new request's page.
        form_errors = self.page.locator(".message.is-danger").all_inner_texts()
        self.assertEqual([], form_errors, "the form was rejected")
        expect(self.page.get_by_text("¡Se creó tu pedido exitosamente!")).to_be_visible()
        help_request = HelpRequest.objects.get(title=title)
        self.assertRegex(self.page.url, rf"/pedidos/{help_request.pk}$")
        self.assertEqual(["viveres"], [c.code for c in help_request.categories.all()])
        self.assertNoJavaScriptErrors()

        # /pedidos fetches the requests inside the visible map area.
        with self.page.expect_response(lambda r: "/api/v1/helprequestsgeo/" in r.url) as geo:
            self.page.goto(self.url("/pedidos"))
        self.assertEqual(200, geo.value.status)
        self.assertIn(help_request.pk, [f["properties"]["pk"] for f in geo.value.json()["features"]])
        # Check for script errors before looking at the map, because a broken
        # script (such as a missing markercluster) is the likely cause there.
        self.page.wait_for_load_state("networkidle")
        self.assertNoJavaScriptErrors()

        # The request is drawn on the map, and its popup links to it ...
        marker = self.page.locator("#main .leaflet-marker-pane .leaflet-marker-icon")
        expect(marker).to_have_count(1)
        marker.click()
        popup = self.page.locator(".leaflet-popup-content")
        expect(popup).to_contain_text(title)
        expect(popup.locator(f'a[href="/pedidos/{help_request.pk}"]').first).to_be_visible()

        # ... and listed in the table under the map.
        expect(self.page.locator("#table")).to_contain_text(title)
        self.assertNoJavaScriptErrors()

    def test_the_form_refuses_a_request_without_a_location(self):
        self.page.goto(self.url("/solicitar"))
        self.page.fill("#id_title", "Sin ubicación")
        self.page.fill("#id_message", "Mensaje")
        self.page.fill("#id_name", "María Prueba")
        self.page.fill("#id_phone", "0981555124")
        self.page.fill("#id_address", "Calle Palma 123")
        self.page.click("#submit")

        expect(self.page.get_by_text("You forgot to mark your location on the map").or_(
            self.page.get_by_text("Te olvidaste de marcar tu ubicación en el mapa")
        ).first).to_be_visible()
        self.assertFalse(HelpRequest.objects.filter(title="Sin ubicación").exists())

    # Anyone can create a help request, so names and titles are untrusted.
    # The map popups must show them as text, never run them as HTML.
    XSS_PAYLOAD = '<img src="x" onerror="window.__xss = (window.__xss || 0) + 1">'

    def assertPopupShowsTextOnly(self, path, text):
        self.page.goto(self.url(path))
        self.page.wait_for_load_state("networkidle")
        self.page.locator("#main .leaflet-marker-pane .leaflet-marker-icon").first.click()

        popup = self.page.locator(".leaflet-popup-content")
        expect(popup).to_be_visible()
        self.page.wait_for_load_state("networkidle")  # let a broken <img> fire onerror
        self.assertIsNone(self.page.evaluate("window.__xss"), f"the popup on {path} ran injected JavaScript")
        self.assertEqual(0, popup.locator("img").count(), f"the popup on {path} rendered HTML from the data")
        expect(popup).to_contain_text(text)  # shown literally, as text
        self.assertNoJavaScriptErrors()

    def test_help_request_popups_escape_html(self):
        # Submitted through the public form, as an attacker would.
        self.fill_request_form(self.XSS_PAYLOAD)
        self.page.click("#submit")
        expect(self.page.get_by_text("¡Se creó tu pedido exitosamente!")).to_be_visible()

        for path in ("/pedidos", "/pedidos_ciudad/Asuncion"):
            with self.subTest(path=path):
                self.assertPopupShowsTextOnly(path, self.XSS_PAYLOAD)

    def test_donation_center_popups_escape_html(self):
        lon, lat = settings.LEAFLET_CONFIG["DEFAULT_CENTER"][::-1]
        make_donation_center(name=self.XSS_PAYLOAD, location=Point(lon, lat, srid=4326))

        for path in ("/donaciones", "/donaciones_ciudad/Asuncion"):
            with self.subTest(path=path):
                self.assertPopupShowsTextOnly(path, self.XSS_PAYLOAD)
        self.assertNoJavaScriptErrors()
