"""Guards against third-party JS/CSS that the site loads from other hosts.

These assets can break without any change to this repository: in 2026 the
``leaflet.github.io`` copy of ``leaflet.markercluster-src.js`` started returning
404, ``L.markerClusterGroup`` became undefined and the maps on /pedidos and
/donaciones silently stopped showing markers.

* ``ExternalAssetPinningTests`` run offline with the rest of the suite. They
  require every external script and stylesheet to name an exact version, so
  nobody can upgrade it from under us or move it to a new path.
* ``ExternalAssetAvailabilityTests`` fetch every asset over the network and run
  only when ``CHECK_EXTERNAL_ASSETS=1`` is set. The *External assets* workflow
  runs them every day, because breakage like the one above appears without
  any push to the repository.
"""
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from core.tests.helpers import make_help_request, mock_geocoder
from org.tests.test_views import make_donation_center

# Pages that render every template that loads external assets. The map pages
# matter most: their list scripts call L.markerClusterGroup().
PAGES = [
    "/",
    "/pedidos",
    "/donaciones",
    "/pedidos_ciudad/Asuncion",
    "/donaciones_ciudad/Asuncion",
    "/solicitar",
    "/ceder",
    "/stats",
    "/preguntas_frecuentes",
    "/legal",
    "/contacto",
    "/voluntario",
]
MAP_PAGES = ["/pedidos", "/donaciones", "/pedidos_ciudad/Asuncion", "/donaciones_ciudad/Asuncion"]

# Hosts that serve content which has no versioned URL by design.
UNVERSIONED_HOSTS = {"www.googletagmanager.com"}

# A version in the path, such as "@0.8.0", "/1.5.3/" or "v5.3.1".
VERSION_RE = re.compile(r"[@/v]\d+\.\d+(\.\d+)?([/.,-]|$)")


class _AssetParser(HTMLParser):
    """Collects the external ``<script src>`` and stylesheet ``<link href>`` URLs."""

    def __init__(self):
        super().__init__()
        self.assets = set()  # {(kind, url)}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self._add("script", attrs["src"])
        elif tag == "link" and "stylesheet" in (attrs.get("rel") or "").split() and attrs.get("href"):
            self._add("stylesheet", attrs["href"])

    def _add(self, kind, url):
        if url.startswith("//"):
            url = "https:" + url
        if url.startswith(("http://", "https://")):
            self.assets.add((kind, url))


def _leaflet_plugin_assets():
    """The external assets declared in ``LEAFLET_CONFIG['PLUGINS']``."""
    assets = set()
    for plugin in settings.LEAFLET_CONFIG.get("PLUGINS", {}).values():
        if not isinstance(plugin, dict):  # django-leaflet adds bookkeeping entries
            continue
        for key, kind in (("js", "script"), ("css", "stylesheet")):
            urls = plugin.get(key, [])
            for url in [urls] if isinstance(urls, str) else urls:
                if url.startswith(("http://", "https://", "//")):
                    assets.add((kind, url))
    return assets


class _ExternalAssetsMixin:
    @classmethod
    def setUpTestData(cls):
        # The city pages return 500 for a city with nothing in it.
        with mock_geocoder({"city": "Asunción"}):
            make_help_request()
        make_donation_center()
        # /stats and /ceder are only for logged-in staff.
        cls.admin = User.objects.create_superuser("admin", password="secret")

    def collect_assets(self, pages=PAGES):
        """``{(kind, url): first page that loads it}`` for the given pages."""
        found = {}
        self.client.force_login(self.admin)
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(200, response.status_code, f"{page} did not render")
            parser = _AssetParser()
            parser.feed(response.content.decode())
            for asset in parser.assets:
                found.setdefault(asset, page)
        for asset in _leaflet_plugin_assets():
            found.setdefault(asset, "LEAFLET_CONFIG")
        return found


class ExternalAssetPinningTests(_ExternalAssetsMixin, TestCase):
    def test_finds_external_assets(self):
        # Guards the tests below: if the parser stops finding assets, they
        # pass without checking anything.
        self.assertTrue(any("markercluster" in url for _, url in self.collect_assets()))

    def test_external_assets_use_https(self):
        for (kind, url), page in self.collect_assets().items():
            with self.subTest(url=url, page=page):
                self.assertTrue(url.startswith("https://"), f"{kind} on {page} is not loaded over HTTPS")

    def test_external_assets_pin_an_exact_version(self):
        for (kind, url), page in self.collect_assets().items():
            host = urllib.parse.urlsplit(url).hostname
            if host in UNVERSIONED_HOSTS:
                continue
            with self.subTest(url=url, page=page):
                self.assertRegex(
                    urllib.parse.urlsplit(url).path,
                    VERSION_RE,
                    f"{kind} on {page} has no version in its URL; pin one "
                    "(for example from cdnjs or jsdelivr) or serve it from static/",
                )

    def test_map_pages_load_markercluster(self):
        # static/scripts/list.js and list-donation.js call L.markerClusterGroup().
        for page in MAP_PAGES:
            with self.subTest(page=page):
                scripts = [url for kind, url in self.collect_assets([page]) if kind == "script"]
                self.assertTrue(
                    any("markercluster" in url for url in scripts),
                    f"{page} does not load the Leaflet.markercluster script",
                )


@skipUnless(os.environ.get("CHECK_EXTERNAL_ASSETS") == "1", "set CHECK_EXTERNAL_ASSETS=1 to fetch external assets")
class ExternalAssetAvailabilityTests(_ExternalAssetsMixin, TestCase):
    EXPECTED_CONTENT_TYPE = {"script": "javascript", "stylesheet": "text/css"}

    def test_external_assets_are_reachable(self):
        for (kind, url), page in sorted(self.collect_assets().items()):
            with self.subTest(url=url, page=page):
                request = urllib.request.Request(url, headers={"User-Agent": "ayudapy-asset-check"})
                try:
                    with urllib.request.urlopen(request, timeout=20) as response:
                        status = response.status
                        content_type = response.headers.get("Content-Type", "")
                except urllib.error.HTTPError as error:
                    self.fail(f"{kind} on {page} returned HTTP {error.code}")
                except urllib.error.URLError as error:
                    self.fail(f"{kind} on {page} could not be fetched: {error.reason}")

                self.assertEqual(200, status, f"{kind} on {page} returned HTTP {status}")
                self.assertIn(
                    self.EXPECTED_CONTENT_TYPE[kind],
                    content_type,
                    f"{kind} on {page} was served as {content_type!r}",
                )
