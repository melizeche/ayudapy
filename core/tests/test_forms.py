"""Tests for :class:`core.forms.HelpRequestForm`."""
from core.models import Category, HelpRequest
from core.tests.helpers import GeocodedTestCase, make_image

WKT_ASUNCION = "SRID=4326;POINT (-57.5759 -25.2637)"


def form_data(**overrides):
    data = {
        "title": "Necesito comida",
        "message": "Somos cuatro en casa y no tenemos qué comer",
        "name": "Juan Pérez",
        "phone": "0981 123 456",
        "address": "Calle Palma 123",
        "location": WKT_ASUNCION,
    }
    data.update(overrides)
    return data


class HelpRequestFormValidationTests(GeocodedTestCase):
    def test_accepts_a_complete_submission(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_saving_creates_a_geocoded_help_request(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data())
        self.assertTrue(form.is_valid(), form.errors)
        help_request = form.save()

        self.assertEqual(HelpRequest.objects.count(), 1)
        self.assertEqual(help_request.city, "Asunción")
        self.assertEqual(help_request.phone, "0981123456")
        self.assertAlmostEqual(help_request.location.x, -57.5759, places=4)

    def test_location_is_required(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data(location=""))
        self.assertFalse(form.is_valid())
        self.assertIn("location", form.errors)

    def test_missing_location_uses_the_custom_error_message(self):
        """The map field replaces Django's generic "this field is required"."""
        from core.forms import HelpRequestForm

        # Compared against the configured message rather than a literal string:
        # the catalogs are compiled per checkout, so the language varies.
        expected = HelpRequestForm().fields["location"].error_messages["required"]
        form = HelpRequestForm(data=form_data(location=""))

        form.is_valid()
        self.assertEqual([expected], form.errors["location"])

    def test_title_name_and_phone_are_required(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data(title="", name="", phone=""))
        self.assertFalse(form.is_valid())
        for field in ("title", "name", "phone"):
            self.assertIn(field, form.errors)

    def test_rejects_a_title_longer_than_the_model_allows(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data(title="x" * 201))
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_picture_and_categories_are_optional(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(form.fields["picture"].required)
        self.assertFalse(form.fields["categories"].required)

    def test_categories_can_be_selected(self):
        from core.forms import HelpRequestForm

        Category.objects.create(code="comida", name="Comida")
        form = HelpRequestForm(data=form_data(categories=["comida"]))
        self.assertTrue(form.is_valid(), form.errors)
        help_request = form.save()
        self.assertEqual(["comida"], [c.code for c in help_request.categories.all()])

    def test_rejects_an_unknown_category(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data(categories=["inexistente"]))
        self.assertFalse(form.is_valid())
        self.assertIn("categories", form.errors)

    def test_accepts_an_uploaded_picture(self):
        from core.forms import HelpRequestForm

        form = HelpRequestForm(data=form_data(), files={"picture": make_image()})
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_a_file_that_is_not_an_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from core.forms import HelpRequestForm

        not_an_image = SimpleUploadedFile("virus.jpg", b"definitely not an image")
        form = HelpRequestForm(data=form_data(), files={"picture": not_an_image})
        self.assertFalse(form.is_valid())
        self.assertIn("picture", form.errors)

    def test_only_the_public_fields_are_exposed(self):
        from core.forms import HelpRequestForm

        self.assertEqual(
            ["title", "message", "categories", "name", "phone", "location", "address", "picture"],
            list(HelpRequestForm().fields),
        )
