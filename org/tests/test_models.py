"""Tests for the ``org`` models (donation centers, volunteers, pools)."""
from django.contrib.auth.models import User
from django.test import TestCase

from core.tests.helpers import ASUNCION, mock_geocoder
from org.models import DEP, DonationCenter, Organization, Pool, Profile


def build_and_save(model, **kwargs):
    """Instantiate and save ``model``.

    ``DonationCenter.save()`` and ``BaseResource.save()`` take no arguments, so
    ``Model.objects.create()`` (which passes ``force_insert=True``) raises a
    ``TypeError``. Saving the instance directly is the path the forms take.
    """
    instance = model(**kwargs)
    instance.save()
    return instance


class OrganizationTests(TestCase):
    def test_str_is_the_name(self):
        self.assertEqual("Cruz Roja", str(Organization.objects.create(name="Cruz Roja")))


class DonationCenterTests(TestCase):
    def make(self, **kwargs):
        kwargs.setdefault("name", "Centro de acopio")
        kwargs.setdefault("phone", "0981 123 456")
        kwargs.setdefault("address", "Calle Palma 123")
        kwargs.setdefault("location", ASUNCION)
        return build_and_save(DonationCenter, **kwargs)

    def test_city_is_resolved_on_save(self):
        with mock_geocoder({"city": "Asunción"}):
            center = self.make()
        self.assertEqual("Asunción", center.city)
        self.assertEqual("Asuncion", center.city_code)

    def test_city_code_is_an_ascii_slug(self):
        with mock_geocoder({"city": "Ñemby Vieja"}):
            center = self.make()
        self.assertEqual("Nemby_Vieja", center.city_code)

    def test_falls_back_to_town_then_locality(self):
        with mock_geocoder({"town": "Luque"}):
            self.assertEqual("Luque", self.make().city)
        with mock_geocoder({"locality": "Areguá"}):
            self.assertEqual("Areguá", self.make().city)

    def test_unknown_address_shape_leaves_the_city_empty(self):
        with mock_geocoder({"country": "Paraguay"}):
            center = self.make()
        self.assertEqual("", center.city)

    def test_spaces_are_stripped_from_the_phone_number(self):
        with mock_geocoder({"city": "Asunción"}):
            center = self.make(phone="0981 123 456")
        self.assertEqual("0981123456", center.phone)

    def test_str_includes_the_id_name_and_city(self):
        with mock_geocoder({"city": "Asunción"}):
            center = self.make(name="Centro de acopio")
        self.assertEqual(f"<Centro #{center.id} - Centro de acopio> - Asunción", str(center))

    def test_centers_start_active(self):
        with mock_geocoder({"city": "Asunción"}):
            center = self.make()
        self.assertTrue(center.active)
        self.assertIsNotNone(center.added)

    def test_history_is_recorded(self):
        with mock_geocoder({"city": "Asunción"}):
            center = self.make(name="Original")
            center.name = "Editado"
            center.save()
        self.assertEqual(2, center.history.count())

    def test_verbose_names_are_spanish(self):
        self.assertEqual("Centro de Donación", DonationCenter._meta.verbose_name)
        self.assertEqual("Centros de Donación", DonationCenter._meta.verbose_name_plural)


class ProfileTests(TestCase):
    def make(self, **kwargs):
        kwargs.setdefault("user", User.objects.create_user("voluntario", password="secret"))
        kwargs.setdefault("name", "Ana Giménez")
        kwargs.setdefault("phone", "0981123456")
        kwargs.setdefault("location", ASUNCION)
        kwargs.setdefault("department", 0)
        kwargs.setdefault("address", "Calle Palma 123")
        return build_and_save(Profile, **kwargs)

    def test_city_is_resolved_on_save(self):
        with mock_geocoder({"city": "Asunción"}):
            profile = self.make()
        self.assertEqual("Asunción", profile.city)
        self.assertEqual("Asuncion", profile.city_code)

    def test_str_is_the_volunteer_name(self):
        with mock_geocoder({"city": "Asunción"}):
            self.assertEqual("Ana Giménez", str(self.make()))

    def test_department_choices_cover_every_paraguayan_department(self):
        self.assertEqual(18, len(DEP))
        self.assertIn((0, "Asuncion"), DEP)

    def test_is_linked_one_to_one_with_an_auth_user(self):
        user = User.objects.create_user("otra", password="secret")
        with mock_geocoder({"city": "Asunción"}):
            profile = self.make(user=user)
        self.assertEqual(profile, user.profile)


class PoolTests(TestCase):
    def make(self, **kwargs):
        kwargs.setdefault("name", "Carlos Benítez")
        kwargs.setdefault("phone", "0981 123 456")
        kwargs.setdefault("location", ASUNCION)
        kwargs.setdefault("address", "Calle Palma 123")
        return build_and_save(Pool, **kwargs)

    def test_inherits_the_geocoding_behaviour_of_base_resource(self):
        with mock_geocoder({"city": "Asunción"}):
            pool = self.make()
        self.assertEqual("Asunción", pool.city)
        self.assertEqual("Asuncion", pool.city_code)
        self.assertEqual("0981123456", pool.phone)

    def test_str_includes_the_id_name_and_city(self):
        with mock_geocoder({"city": "Asunción"}):
            pool = self.make(name="Carlos Benítez")
        self.assertEqual(f"<Piscina #{pool.id} - Carlos Benítez> - Asunción", str(pool))

    def test_info_is_optional(self):
        with mock_geocoder({"city": "Asunción"}):
            pool = self.make(info="20.000 litros")
        self.assertEqual("20.000 litros", pool.info)
        with mock_geocoder({"city": "Asunción"}):
            self.assertIsNone(self.make().info)
