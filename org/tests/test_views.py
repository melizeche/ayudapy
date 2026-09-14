"""Tests for the ``org`` views.

Donation centers are curated: only users holding ``org.add_donationcenter`` may
publish one, while the listings themselves are public.
"""
import base64

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from core.tests.helpers import ASUNCION, ENCARNACION, mock_geocoder
from org.models import DonationCenter
from org.tests.test_models import build_and_save

WKT_ASUNCION = "SRID=4326;POINT (-57.5759 -25.2637)"


def make_donation_center(city="Asunción", **kwargs):
    kwargs.setdefault("name", "Centro de acopio")
    kwargs.setdefault("phone", "0981123456")
    kwargs.setdefault("address", "Calle Palma 123")
    kwargs.setdefault("location", ASUNCION)
    with mock_geocoder({"city": city}):
        return build_and_save(DonationCenter, **kwargs)


class DonationPermissionTestCase(TestCase):
    def login_with_permission(self):
        user = User.objects.create_user("encargado", password="secret")
        user.user_permissions.add(Permission.objects.get(codename="add_donationcenter"))
        self.client.login(username="encargado", password="secret")
        return user

    def login_without_permission(self):
        User.objects.create_user("visitante", password="secret")
        self.client.login(username="visitante", password="secret")


class DonationFormViewTests(DonationPermissionTestCase):
    url = reverse("donation-form")

    def test_anonymous_visitors_are_sent_to_the_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
        self.assertIn("/accounts/login/", response["Location"])

    def test_a_user_without_the_permission_is_refused(self):
        self.login_without_permission()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)

    def test_an_authorised_user_gets_the_form(self):
        self.login_with_permission()
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "donation_center/create.html")
        self.assertEqual(
            ["name", "phone", "location", "address"],
            list(response.context["form"].fields),
        )

    def test_a_valid_post_creates_the_center_and_redirects_to_it(self):
        self.login_with_permission()
        data = {
            "name": "Centro de acopio",
            "phone": "0981 123 456",
            "address": "Calle Palma 123",
            "location": WKT_ASUNCION,
        }

        with mock_geocoder({"city": "Asunción"}):
            response = self.client.post(self.url, data)

        center = DonationCenter.objects.get()
        self.assertRedirects(
            response,
            reverse("donaciones-detail", args=[center.pk]),
            fetch_redirect_response=False,
        )
        self.assertEqual("Asunción", center.city)
        self.assertEqual("0981123456", center.phone)

    def test_an_invalid_post_redisplays_the_form(self):
        self.login_with_permission()
        with mock_geocoder({"city": "Asunción"}):
            response = self.client.post(self.url, {"name": "", "location": WKT_ASUNCION})

        self.assertEqual(200, response.status_code)
        self.assertIn("name", response.context["form"].errors)
        self.assertEqual(0, DonationCenter.objects.count())


class RestrictedViewTests(DonationPermissionTestCase):
    def test_anonymous_visitors_are_refused(self):
        response = self.client.get("/donar")
        self.assertEqual(302, response.status_code)

    def test_an_authorised_user_sees_the_page(self):
        self.login_with_permission()
        response = self.client.get("/donar")
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "donation_center/info.html")


class ViewDonationCenterTests(TestCase):
    def test_renders_an_existing_center(self):
        center = make_donation_center(name="Centro de acopio")

        response = self.client.get(reverse("donaciones-detail", args=[center.pk]))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "donation_center/details.html")
        self.assertEqual(center.pk, response.context["donation_center"].pk)
        self.assertEqual("Centro de acopio", response.context["name"])

    def test_unknown_center_returns_404(self):
        self.assertEqual(404, self.client.get(reverse("donaciones-detail", args=[99999])).status_code)

    def test_the_phone_number_is_rendered_as_an_image(self):
        center = make_donation_center()
        response = self.client.get(reverse("donaciones-detail", args=[center.pk]))
        self.assertTrue(base64.b64decode(response.context["phone_number_img"]).startswith(b"\x89PNG"))

    def test_the_whatsapp_link_uses_the_paraguayan_country_code(self):
        center = make_donation_center(phone="0981123456")
        response = self.client.get(reverse("donaciones-detail", args=[center.pk]))
        self.assertTrue(response.context["whatsapp"].startswith("595981123456?text="))

    def test_a_center_without_a_phone_number_hides_the_contact_details(self):
        center = make_donation_center()
        # Set afterwards: DonationCenter.save() cannot cope with a null phone.
        DonationCenter.objects.filter(pk=center.pk).update(phone=None)

        response = self.client.get(reverse("donaciones-detail", args=[center.pk]))

        self.assertEqual(200, response.status_code)
        self.assertIsNone(response.context["phone_number_img"])
        self.assertIsNone(response.context["whatsapp"])


class ListDonationViewTests(TestCase):
    def test_lists_the_cities_that_have_centers(self):
        make_donation_center(city="Asunción")
        make_donation_center(city="Luque")

        response = self.client.get("/donaciones")

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "donation_center/list.html")
        self.assertEqual(
            [("Asunción", "Asuncion"), ("Luque", "Luque")],
            sorted(response.context["list_donation_cities"]),
        )

    def test_each_city_is_listed_once(self):
        make_donation_center()
        make_donation_center()
        response = self.client.get("/donaciones")
        self.assertEqual(1, len(response.context["list_donation_cities"]))

    def test_renders_with_no_centers_at_all(self):
        response = self.client.get("/donaciones")
        self.assertEqual([], response.context["list_donation_cities"])


class ListDonationByCityViewTests(TestCase):
    url = reverse("donation-by-city", args=["Asuncion"])

    def test_lists_the_centers_of_one_city_only(self):
        wanted = make_donation_center(city="Asunción")
        make_donation_center(city="Luque")

        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "donation_center/list_by_city.html")
        self.assertEqual([wanted.pk], [c.pk for c in response.context["list_donations"]])
        self.assertEqual("Asunción", response.context["city"])

    def test_newest_centers_come_first(self):
        older = make_donation_center()
        newer = make_donation_center()
        response = self.client.get(self.url)
        self.assertEqual([newer.pk, older.pk], [c.pk for c in response.context["list_donations"]])

    def test_exposes_the_centers_as_geojson_for_the_map(self):
        import json

        center = make_donation_center(name="Centro de acopio")

        response = self.client.get(self.url)

        geo = json.loads(response.context["geo"])
        self.assertEqual("FeatureCollection", geo["type"])
        self.assertEqual(1, len(geo["features"]))
        self.assertEqual("Centro de acopio", geo["features"][0]["properties"]["name"])
        self.assertEqual(center.location.x, geo["features"][0]["geometry"]["coordinates"][0])

    def test_paginates_at_twenty_five_per_page(self):
        for index in range(26):
            make_donation_center(name=f"Centro {index}")

        first_page = self.client.get(self.url)
        second_page = self.client.get(self.url, {"page": 2})

        self.assertEqual(25, len(first_page.context["list_paginated"]))
        self.assertEqual(1, len(second_page.context["list_paginated"]))

    def test_a_non_numeric_page_falls_back_to_the_first_one(self):
        make_donation_center()
        response = self.client.get(self.url, {"page": "abc"})
        self.assertEqual(1, response.context["list_paginated"].number)

    def test_a_page_past_the_end_falls_back_to_the_last_one(self):
        make_donation_center()
        response = self.client.get(self.url, {"page": 99})
        self.assertEqual(1, response.context["list_paginated"].number)
