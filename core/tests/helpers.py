"""Shared helpers for the AyudaPY test suite.

Both ``core`` and ``org`` geocode on every ``save()`` by calling Nominatim over
the network. Tests must never do that, so everything here revolves around
replacing the geocoder with a predictable fake.
"""
import contextlib
import itertools
from io import BytesIO
from unittest import mock

from PIL import Image
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import HelpRequest

# Somewhere in downtown Asunción, the default location for fixtures.
ASUNCION = Point(-57.5759, -25.2637, srid=4326)
# Far enough away to fall outside a bounding box drawn around Asunción.
ENCARNACION = Point(-55.8683, -27.3306, srid=4326)

_phone_numbers = itertools.count(1)


@contextlib.contextmanager
def mock_geocoder(address=None, reverse_side_effect=None, modules=("core.models", "org.models")):
    """Patch ``Nominatim`` so ``_get_city()`` resolves without touching the network.

    :param address: the ``address`` dict Nominatim would have returned, e.g.
        ``{"city": "Asunción"}``. ``None`` yields a response with no address.
    :param reverse_side_effect: raise this instead of answering, to exercise the
        "geolocator unavailable" paths.
    """
    location = mock.Mock()
    location.raw = {"address": address} if address is not None else {}

    with contextlib.ExitStack() as stack:
        for module in modules:
            geolocator = stack.enter_context(mock.patch(f"{module}.Nominatim"))
            if reverse_side_effect is not None:
                geolocator.return_value.reverse.side_effect = reverse_side_effect
            else:
                geolocator.return_value.reverse.return_value = location
        yield


class GeocodedTestCase(TestCase):
    """A ``TestCase`` whose geocoder always answers with ``geocoded_city``."""

    geocoded_city = "Asunción"

    def setUp(self):
        super().setUp()
        self.use_geocoder({"city": self.geocoded_city})

    def use_geocoder(self, address=None, reverse_side_effect=None):
        """(Re)install the fake geocoder for the remainder of the test."""
        for patcher in getattr(self, "_geocoder_patchers", []):
            patcher.__exit__(None, None, None)
        patcher = mock_geocoder(address, reverse_side_effect)
        patcher.__enter__()
        self._geocoder_patchers = [patcher]
        self.addCleanup(self._stop_geocoder, patcher)

    def _stop_geocoder(self, patcher):
        if patcher in getattr(self, "_geocoder_patchers", []):
            patcher.__exit__(None, None, None)
            self._geocoder_patchers.remove(patcher)


def unique_phone():
    """A fresh phone number.

    ``HelpRequest.save()`` deactivates every earlier request sharing a phone
    number, so fixtures that are meant to coexist need distinct ones.
    """
    return "0981{:06d}".format(next(_phone_numbers))


def make_help_request(**kwargs):
    """Create a saved :class:`~core.models.HelpRequest` with sane defaults."""
    kwargs.setdefault("title", "Necesito ayuda")
    kwargs.setdefault("message", "Descripción del pedido")
    kwargs.setdefault("name", "Juan Pérez")
    kwargs.setdefault("phone", unique_phone())
    kwargs.setdefault("address", "Calle Palma 123")
    kwargs.setdefault("location", ASUNCION)
    return HelpRequest.objects.create(**kwargs)


def make_image(name="foto.jpg", size=(800, 600), fmt="JPEG", color=(200, 30, 30)):
    """An in-memory uploaded image file, for ``picture`` fields."""
    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, fmt)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=f"image/{fmt.lower()}")
