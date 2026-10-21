"""Tests for the ``core`` models: geocoding on save, duplicate handling,
full-text search and the thumbnail signal."""
import os
import shutil
import tempfile
from unittest import mock

from django.test import TestCase, override_settings

from core.models import Category, FrequentAskedQuestion, HelpRequest
from core.tests.helpers import ASUNCION, GeocodedTestCase, make_help_request, make_image


class CategoryTests(TestCase):
    def test_str_is_the_readable_name(self):
        category = Category.objects.create(code="comida", name="Comida")
        self.assertEqual(str(category), "Comida")

    def test_defaults(self):
        category = Category.objects.create(code="salud", name="Salud")
        self.assertEqual(category.color, "#000000")
        self.assertTrue(category.active)


class FrequentAskedQuestionTests(TestCase):
    def test_str_is_the_question(self):
        faq = FrequentAskedQuestion.objects.create(order="1", question="¿Cómo ayudo?", answer="Así")
        self.assertEqual(str(faq), "¿Cómo ayudo?")

    def test_default_ordering_follows_the_order_field(self):
        FrequentAskedQuestion.objects.create(order="2", question="Segunda", answer="b")
        FrequentAskedQuestion.objects.create(order="1", question="Primera", answer="a")
        self.assertEqual(
            ["Primera", "Segunda"],
            list(FrequentAskedQuestion.objects.values_list("question", flat=True)),
        )

    def test_uses_the_legacy_table_name(self):
        self.assertEqual(FrequentAskedQuestion._meta.db_table, "core_faq")


class HelpRequestGeocodingTests(GeocodedTestCase):
    def test_city_is_resolved_on_save(self):
        help_request = make_help_request()
        self.assertEqual(help_request.city, "Asunción")

    def test_city_code_is_an_ascii_slug_of_the_city(self):
        self.use_geocoder({"city": "Ñemby Vieja"})
        help_request = make_help_request()
        self.assertEqual(help_request.city, "Ñemby Vieja")
        self.assertEqual(help_request.city_code, "Nemby_Vieja")

    def test_falls_back_to_town_when_there_is_no_city(self):
        self.use_geocoder({"town": "Luque"})
        self.assertEqual(make_help_request().city, "Luque")

    def test_falls_back_to_locality_when_there_is_no_city_or_town(self):
        self.use_geocoder({"locality": "Areguá"})
        self.assertEqual(make_help_request().city, "Areguá")

    def test_unknown_address_shape_leaves_the_city_empty(self):
        self.use_geocoder({"country": "Paraguay"})
        help_request = make_help_request()
        self.assertEqual(help_request.city, "")
        self.assertEqual(help_request.city_code, "")

    def test_geocoder_failure_does_not_break_saving(self):
        self.use_geocoder(reverse_side_effect=OSError("Nominatim is down"))
        with self.assertLogs("core.models", level="ERROR") as logs:
            help_request = make_help_request()
        self.assertEqual(help_request.city, "")
        self.assertIn("Geolocator unavailable", logs.output[0])


class HelpRequestSaveTests(GeocodedTestCase):
    def test_spaces_are_stripped_from_the_phone_number(self):
        help_request = make_help_request(phone="0981 123 456")
        self.assertEqual(help_request.phone, "0981123456")

    def test_creating_a_request_deactivates_previous_ones_with_the_same_phone(self):
        first = make_help_request(phone="0981111111", title="Pedido viejo")
        second = make_help_request(phone="0981111111", title="Pedido nuevo")

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.active)
        self.assertTrue(second.active)

    def test_requests_with_different_phones_stay_active(self):
        first = make_help_request(phone="0981111111")
        make_help_request(phone="0982222222")

        first.refresh_from_db()
        self.assertTrue(first.active)

    def test_updating_a_request_does_not_deactivate_itself(self):
        help_request = make_help_request(phone="0981111111")
        help_request.title = "Título editado"
        help_request.save()

        help_request.refresh_from_db()
        self.assertTrue(help_request.active)
        self.assertEqual(help_request.title, "Título editado")

    def test_str_includes_the_id_and_the_name(self):
        help_request = make_help_request(name="María López")
        self.assertEqual(str(help_request), f"<Pedido #{help_request.id} - María López>")

    def test_new_requests_start_unresolved_and_unvoted(self):
        help_request = make_help_request()
        self.assertTrue(help_request.active)
        self.assertFalse(help_request.resolved)
        self.assertEqual(help_request.upvotes, 0)
        self.assertEqual(help_request.downvotes, 0)
        self.assertIsNotNone(help_request.added)


class HelpRequestPictureTests(GeocodedTestCase):
    def setUp(self):
        super().setUp()
        # MEDIA_ROOT needs the trailing separator: the thumbnail signal builds
        # its path by concatenating MEDIA_ROOT with the picture name.
        self.media_root = tempfile.mkdtemp() + os.sep
        self.addCleanup(shutil.rmtree, self.media_root, True)
        overridden = override_settings(MEDIA_ROOT=self.media_root)
        overridden.enable()
        self.addCleanup(overridden.disable)

    def test_thumb_points_at_the_th_suffixed_file(self):
        help_request = make_help_request(picture=make_image("pedido.jpg"))
        self.assertEqual(help_request.thumb, help_request.picture.url.replace(".jpg", "_th.jpg"))

    def test_saving_with_a_picture_generates_a_thumbnail(self):
        help_request = make_help_request(picture=make_image("pedido.jpg"))
        thumbnail = os.path.join(self.media_root, str(help_request.picture)).replace(".jpg", "_th.jpg")
        self.assertTrue(os.path.exists(thumbnail))

    def test_saving_without_a_picture_skips_thumbnail_generation(self):
        with mock.patch("core.models.create_thumbnail") as create_thumbnail:
            make_help_request()
        create_thumbnail.assert_not_called()

    def test_thumbnail_errors_are_logged_and_swallowed(self):
        with mock.patch("core.models.create_thumbnail", side_effect=OSError("disk full")):
            with self.assertLogs("core.models", level="ERROR") as logs:
                help_request = make_help_request(picture=make_image("pedido.jpg"))
        self.assertIsNotNone(help_request.pk)
        self.assertIn("Error creating thumbnail", logs.output[0])


class HelpRequestSearchTests(GeocodedTestCase):
    def test_search_vector_is_populated_by_the_database_trigger(self):
        make_help_request(title="Necesito comida")
        self.assertTrue(HelpRequest.objects.values_list("search_vector", flat=True).first())

    def test_matches_words_in_the_title(self):
        wanted = make_help_request(title="Necesito comida para mi familia")
        make_help_request(title="Necesito frazadas", message="hace frío")

        results = HelpRequest.objects.filter_by_search_query("comida")
        self.assertEqual([wanted.pk], [r.pk for r in results])

    def test_matches_words_in_the_message(self):
        wanted = make_help_request(title="Pedido urgente", message="Nos falta comida")
        results = HelpRequest.objects.filter_by_search_query("comida")
        self.assertEqual([wanted.pk], [r.pk for r in results])

    def test_matches_on_the_spanish_stem_of_the_word(self):
        wanted = make_help_request(title="Necesitamos medicamentos")
        results = HelpRequest.objects.filter_by_search_query("medicamento")
        self.assertEqual([wanted.pk], [r.pk for r in results])

    def test_title_matches_outrank_message_matches(self):
        in_message = make_help_request(title="Pedido urgente", message="Nos falta comida")
        in_title = make_help_request(title="Necesito comida", message="Gracias")

        results = list(HelpRequest.objects.filter_by_search_query("comida"))
        self.assertEqual([in_title.pk, in_message.pk], [r.pk for r in results])
        self.assertGreater(results[0].rank, results[1].rank)

    def test_returns_nothing_when_no_request_matches(self):
        make_help_request(title="Necesito frazadas")
        self.assertEqual(0, HelpRequest.objects.filter_by_search_query("comida").count())


class HelpRequestRelationTests(GeocodedTestCase):
    def test_categories_can_be_attached(self):
        category = Category.objects.create(code="comida", name="Comida")
        help_request = make_help_request()
        help_request.categories.add(category)
        self.assertEqual(["Comida"], [c.name for c in help_request.categories.all()])

    def test_history_is_recorded_for_every_save(self):
        help_request = make_help_request(title="Original")
        help_request.title = "Editado"
        help_request.save()
        self.assertEqual(2, help_request.history.count())
        self.assertEqual("Editado", help_request.history.first().title)

    def test_location_is_stored_as_wgs84(self):
        help_request = make_help_request(location=ASUNCION)
        help_request.refresh_from_db()
        self.assertEqual(4326, help_request.location.srid)
        self.assertAlmostEqual(-57.5759, help_request.location.x, places=4)
