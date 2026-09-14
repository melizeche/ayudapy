"""Tests for the ``core`` views (public site pages)."""
import base64
import json
from unittest import mock

from django.contrib.auth.models import User as AuthUser
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Category, FrequentAskedQuestion, HelpRequest, HelpRequestOwner, User
from core.tests.helpers import GeocodedTestCase, make_help_request
from core.tests.test_forms import form_data

VOTE_COOKIE = "votectrl"


class HomeViewTests(TestCase):
    def test_renders_the_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "home.html")


class FaqViewTests(TestCase):
    def test_lists_only_active_questions(self):
        FrequentAskedQuestion.objects.create(order="1", question="Visible", answer="sí", active=True)
        FrequentAskedQuestion.objects.create(order="2", question="Oculta", answer="no", active=False)

        response = self.client.get(reverse("general_faq"))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "footer/general_faq.html")
        self.assertEqual(["Visible"], [f.question for f in response.context["faq_list"]])

    def test_renders_with_no_questions_at_all(self):
        response = self.client.get(reverse("general_faq"))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["faq_list"]))


class ListRequestsViewTests(GeocodedTestCase):
    def test_lists_the_cities_that_have_open_requests(self):
        make_help_request()
        self.use_geocoder({"city": "Luque"})
        make_help_request()

        response = self.client.get("/pedidos")

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "help_request/list.html")
        self.assertEqual(
            [("Asunción", "Asuncion"), ("Luque", "Luque")],
            sorted(response.context["list_cities"]),
        )

    def test_each_city_is_listed_once(self):
        make_help_request()
        make_help_request()
        response = self.client.get("/pedidos")
        self.assertEqual(1, len(response.context["list_cities"]))

    def test_ignores_resolved_and_inactive_requests(self):
        resolved = make_help_request()
        HelpRequest.objects.filter(pk=resolved.pk).update(resolved=True)
        self.use_geocoder({"city": "Luque"})
        inactive = make_help_request()
        HelpRequest.objects.filter(pk=inactive.pk).update(active=False)

        response = self.client.get("/pedidos")

        self.assertEqual([], response.context["list_cities"])


class ListByCityViewTests(GeocodedTestCase):
    def test_lists_the_requests_of_one_city_only(self):
        wanted = make_help_request(title="Pedido en Asunción")
        self.use_geocoder({"city": "Luque"})
        make_help_request(title="Pedido en Luque")

        response = self.client.get(reverse("pedidos-by-city", args=["Asuncion"]))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "help_request/list_by_city.html")
        self.assertEqual([wanted.pk], [r.pk for r in response.context["list_help"]])
        self.assertEqual("Asunción", response.context["city"])

    def test_newest_requests_come_first(self):
        older = make_help_request(title="Primero")
        newer = make_help_request(title="Segundo")
        response = self.client.get(reverse("pedidos-by-city", args=["Asuncion"]))
        self.assertEqual([newer.pk, older.pk], [r.pk for r in response.context["list_help"]])

    def test_paginates_at_twenty_five_per_page(self):
        for index in range(26):
            make_help_request(title=f"Pedido {index}")

        first_page = self.client.get(reverse("pedidos-by-city", args=["Asuncion"]))
        second_page = self.client.get(reverse("pedidos-by-city", args=["Asuncion"]), {"page": 2})

        self.assertEqual(25, len(first_page.context["list_paginated"]))
        self.assertEqual(1, len(second_page.context["list_paginated"]))
        self.assertEqual(2, first_page.context["list_paginated"].paginator.num_pages)

    def test_a_non_numeric_page_falls_back_to_the_first_one(self):
        make_help_request()
        response = self.client.get(reverse("pedidos-by-city", args=["Asuncion"]), {"page": "abc"})
        self.assertEqual(1, response.context["list_paginated"].number)

    def test_a_page_past_the_end_falls_back_to_the_last_one(self):
        make_help_request()
        response = self.client.get(reverse("pedidos-by-city", args=["Asuncion"]), {"page": 99})
        self.assertEqual(1, response.context["list_paginated"].number)


class ViewRequestTests(GeocodedTestCase):
    def test_renders_an_existing_request(self):
        help_request = make_help_request(name="María López")

        response = self.client.get(reverse("pedidos-detail", args=[help_request.pk]))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "help_request/details.html")
        self.assertEqual(help_request.pk, response.context["help_request"].pk)
        self.assertEqual("María López", response.context["name"])

    def test_unknown_request_returns_404(self):
        response = self.client.get(reverse("pedidos-detail", args=[99999]))
        self.assertEqual(404, response.status_code)

    def test_the_phone_number_is_rendered_as_an_image(self):
        help_request = make_help_request()
        response = self.client.get(reverse("pedidos-detail", args=[help_request.pk]))
        # Scraper protection: the number is only served as a base64 PNG.
        self.assertTrue(base64.b64decode(response.context["phone_number_img"]).startswith(b"\x89PNG"))

    def test_the_whatsapp_link_uses_the_paraguayan_country_code(self):
        help_request = make_help_request(phone="0981123456")
        response = self.client.get(reverse("pedidos-detail", args=[help_request.pk]))
        self.assertTrue(response.context["whatsapp"].startswith("595981123456?text="))

    def test_falls_back_to_the_logo_when_there_is_no_picture(self):
        help_request = make_help_request()
        response = self.client.get(reverse("pedidos-detail", args=[help_request.pk]))
        self.assertEqual("/static/img/logo.jpg", response.context["thumbnail"])

    def test_an_inactive_request_points_at_the_newer_ones(self):
        old = make_help_request(phone="0981111111", title="Pedido viejo")
        new = make_help_request(phone="0981111111", title="Pedido nuevo")

        response = self.client.get(reverse("pedidos-detail", args=[old.pk]))

        self.assertEqual([new.pk], [r.pk for r in response.context["active_requests"]])

    def test_an_active_request_lists_no_alternatives(self):
        help_request = make_help_request()
        response = self.client.get(reverse("pedidos-detail", args=[help_request.pk]))
        self.assertEqual([], list(response.context["active_requests"]))


class VotingTests(GeocodedTestCase):
    """Votes are rate-limited by a base64-encoded cookie of already-voted ids."""

    def setUp(self):
        super().setUp()
        self.help_request = make_help_request()
        self.url = reverse("pedidos-detail", args=[self.help_request.pk])

    def vote_cookie(self, response):
        raw = response.cookies[VOTE_COOKIE].value
        return json.loads(base64.b64decode(raw))

    def test_viewing_the_page_initialises_an_empty_vote_cookie(self):
        response = self.client.get(self.url)
        self.assertEqual({}, self.vote_cookie(response))

    def test_an_upvote_after_viewing_the_page_is_counted(self):
        self.client.get(self.url)
        self.client.post(self.url, {"vote": "up"})

        self.help_request.refresh_from_db()
        self.assertEqual(1, self.help_request.upvotes)
        self.assertEqual(0, self.help_request.downvotes)

    def test_a_downvote_after_viewing_the_page_is_counted(self):
        self.client.get(self.url)
        self.client.post(self.url, {"vote": "down"})

        self.help_request.refresh_from_db()
        self.assertEqual(1, self.help_request.downvotes)
        self.assertEqual(0, self.help_request.upvotes)

    def test_voting_records_the_request_in_the_cookie(self):
        self.client.get(self.url)
        response = self.client.post(self.url, {"vote": "up"})
        self.assertEqual({str(self.help_request.pk): True}, self.vote_cookie(response))

    def test_a_second_vote_from_the_same_browser_is_ignored(self):
        self.client.get(self.url)
        self.client.post(self.url, {"vote": "up"})
        self.client.post(self.url, {"vote": "up"})

        self.help_request.refresh_from_db()
        self.assertEqual(1, self.help_request.upvotes)

    def test_a_vote_on_another_request_is_still_allowed(self):
        other = make_help_request()
        other_url = reverse("pedidos-detail", args=[other.pk])

        self.client.get(self.url)
        self.client.post(self.url, {"vote": "up"})
        self.client.post(other_url, {"vote": "up"})

        other.refresh_from_db()
        self.assertEqual(1, other.upvotes)

    def test_a_corrupted_cookie_does_not_break_the_page(self):
        self.client.cookies[VOTE_COOKIE] = "not-valid-base64-json"
        response = self.client.post(self.url, {"vote": "up"})
        self.assertEqual(200, response.status_code)


class RequestFormViewTests(GeocodedTestCase):
    def test_get_renders_an_empty_form(self):
        response = self.client.get(reverse("request-form"))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "help_request/create.html")
        self.assertFalse(response.context["form"].is_bound)
        self.assertEqual([], response.context["selected_categories"])

    def test_a_valid_post_creates_the_request_and_redirects_to_it(self):
        response = self.client.post(reverse("request-form"), form_data())

        help_request = HelpRequest.objects.get()
        self.assertRedirects(
            response,
            reverse("pedidos-detail", args=[help_request.pk]),
            fetch_redirect_response=False,
        )
        self.assertEqual("Necesito comida", help_request.title)

    def test_a_valid_post_shows_a_success_message(self):
        response = self.client.post(reverse("request-form"), form_data(), follow=True)
        self.assertIn("¡Se creó tu pedido exitosamente!", [str(m) for m in response.context["messages"]])

    def test_an_invalid_post_redisplays_the_form_with_errors(self):
        response = self.client.post(reverse("request-form"), form_data(title=""))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "help_request/create.html")
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(0, HelpRequest.objects.count())

    def test_an_invalid_post_keeps_the_selected_categories(self):
        Category.objects.create(code="comida", name="Comida")
        Category.objects.create(code="salud", name="Salud")

        response = self.client.post(reverse("request-form"), form_data(title="", categories=["comida"]))

        self.assertEqual(["comida"], response.context["selected_categories"])


class StatsViewTests(GeocodedTestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("stats"))
        self.assertEqual(302, response.status_code)
        self.assertIn("/accounts/login/", response["Location"])

    def test_shows_the_summary_to_a_logged_in_user(self):
        AuthUser.objects.create_user("staff", password="secret")
        make_help_request()
        self.client.login(username="staff", password="secret")

        response = self.client.get(reverse("stats"))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "stats/dashboard.html")
        self.assertEqual(1, response.context["datos"]["total_active"])


WITH_AYUDAPY_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "core.middleware.AyudaPYMiddleware",
]


@override_settings(MIDDLEWARE=WITH_AYUDAPY_MIDDLEWARE)
class HelpRequestOwnershipTests(GeocodedTestCase):
    """``set_owner_and_update_values`` links a new request to the visitor's device.

    Note that ``AyudaPYMiddleware`` is **not** in the project's ``MIDDLEWARE``
    setting, so this path is dormant in production; these tests pin the intended
    behaviour by enabling the middleware explicitly.
    """

    def post_request_form(self, **overrides):
        return self.client.post(reverse("request-form"), form_data(**overrides), HTTP_USER_AGENT="Mozilla/5.0")

    def test_the_new_request_is_linked_to_the_visitor(self):
        self.post_request_form()

        owner = HelpRequestOwner.objects.get()
        self.assertEqual(HelpRequest.objects.get().pk, owner.help_request_id)
        self.assertEqual(User.objects.get().pk, owner.user_iid_id)

    def test_an_anonymous_user_is_filled_in_from_the_first_request(self):
        self.post_request_form()

        user = User.objects.get()
        help_request = HelpRequest.objects.get()
        self.assertEqual(help_request.name, user.name)
        self.assertEqual(help_request.phone, user.phone)
        self.assertEqual(help_request.address, user.address)
        self.assertEqual(help_request.city, user.city)
        self.assertEqual(help_request.city_code, user.city_code)
        self.assertEqual(help_request.location, user.location)

    def test_an_already_named_user_is_left_untouched(self):
        self.post_request_form()
        user = User.objects.get()
        User.objects.filter(pk=user.pk).update(name="Nombre existente")

        self.post_request_form(title="Segundo pedido", phone="0982222222", name="Otro nombre")

        user.refresh_from_db()
        self.assertEqual("Nombre existente", user.name)
        self.assertEqual(2, HelpRequestOwner.objects.count())

    def test_a_failure_to_link_does_not_lose_the_request(self):
        with mock.patch("core.views.HelpRequestOwner.save", side_effect=RuntimeError("boom")):
            response = self.post_request_form()

        self.assertEqual(302, response.status_code)
        self.assertEqual(1, HelpRequest.objects.count())
        self.assertEqual(0, HelpRequestOwner.objects.count())
