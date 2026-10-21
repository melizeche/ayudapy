"""Tests for :mod:`core.utils`: thumbnails, upload paths and text images."""
import base64
import os
import time
from io import BytesIO
from types import SimpleNamespace
from unittest import mock

from PIL import Image
from django.test import SimpleTestCase

from core.utils import create_thumbnail, image_to_base64, rename_img, text_to_image


class CreateThumbnailTests(SimpleTestCase):
    def setUp(self):
        import tempfile

        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, self.tmpdir, True)
        self.imagepath = os.path.join(self.tmpdir, "pedido.jpg")
        Image.new("RGB", (1000, 500), (10, 20, 30)).save(self.imagepath)
        self.thumbpath = os.path.join(self.tmpdir, "pedido_th.jpg")

    def test_creates_thumbnail_next_to_the_original(self):
        self.assertTrue(create_thumbnail(self.imagepath, 500))
        self.assertTrue(os.path.exists(self.thumbpath))

    def test_thumbnail_is_resized_keeping_the_aspect_ratio(self):
        create_thumbnail(self.imagepath, 500)
        with Image.open(self.thumbpath) as thumb:
            # 1000x500 scaled to a 500px width halves the height as well.
            self.assertEqual(thumb.size, (500, 250))

    def test_existing_thumbnail_is_not_regenerated(self):
        self.assertTrue(create_thumbnail(self.imagepath, 500))
        self.assertFalse(create_thumbnail(self.imagepath, 250))
        with Image.open(self.thumbpath) as thumb:
            self.assertEqual(thumb.size, (500, 250))

    def test_force_regenerates_an_existing_thumbnail(self):
        create_thumbnail(self.imagepath, 500)
        self.assertTrue(create_thumbnail(self.imagepath, 250, force=True))
        with Image.open(self.thumbpath) as thumb:
            self.assertEqual(thumb.size, (250, 125))

    def test_missing_source_is_swallowed_and_reported_as_failure(self):
        missing = os.path.join(self.tmpdir, "does-not-exist.jpg")
        with self.assertLogs("core.utils", level="ERROR") as logs:
            self.assertFalse(create_thumbnail(missing, 500))
        self.assertIn("Error creaing thumbnail", logs.output[0])


class RenameImgTests(SimpleTestCase):
    def test_uses_the_phone_number_as_prefix(self):
        instance = SimpleNamespace(phone="0981123456")
        with mock.patch.object(time, "strftime", return_value="202001021530"):
            path = rename_img(instance, "mi foto.jpg")
        self.assertEqual(path, "pedidos/0981123456_202001021530_mi_foto.jpg")

    def test_falls_back_to_a_timestamp_when_there_is_no_phone(self):
        instance = SimpleNamespace(phone="")
        with mock.patch.object(time, "strftime", return_value="202001021530"):
            path = rename_img(instance, "mi foto.jpg")
        self.assertEqual(path, "pedidos/202001021530-mi_foto.jpg")

    def test_always_stores_under_the_pedidos_directory(self):
        instance = SimpleNamespace(phone="0981123456")
        self.assertTrue(rename_img(instance, "foto.png").startswith("pedidos/"))


class TextToImageTests(SimpleTestCase):
    def test_renders_an_image_of_the_requested_size(self):
        image = text_to_image("0981 123 456", 300, 50)
        self.assertEqual(image.size, (300, 50))
        self.assertEqual(image.mode, "RGB")

    def test_draws_something_over_the_background(self):
        background = (0, 209, 178)
        image = text_to_image("0981123456", 300, 50)
        colors = {color for _, color in image.getcolors(maxcolors=300 * 50)}
        self.assertIn(background, colors)
        self.assertGreater(len(colors), 1, "expected the text to be drawn")


class ImageToBase64Tests(SimpleTestCase):
    def test_returns_a_decodable_png_payload(self):
        encoded = image_to_base64(Image.new("RGB", (10, 10), (1, 2, 3)))
        self.assertIsInstance(encoded, str)
        with Image.open(BytesIO(base64.b64decode(encoded))) as decoded:
            self.assertEqual(decoded.format, "PNG")
            self.assertEqual(decoded.size, (10, 10))
