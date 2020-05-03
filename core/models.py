import logging
from os import path

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.search import SearchVectorField, SearchQuery, SearchRank
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from geopy.geocoders import Nominatim
from simple_history.models import HistoricalRecords

from core.utils import create_thumbnail, rename_img


logger = logging.getLogger(__name__)
THUMBNAIL_BASEWIDTH = 500


class HelpRequestQuerySet(models.QuerySet):
    def filter_by_search_query(self, query):
        query = SearchQuery(query, config="spanish")
        rank = SearchRank(F("search_vector"), query)
        return self.filter(search_vector=query).annotate(rank=rank).order_by("-rank")

# Category: model ...

class Category(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=30, primary_key=True)
    color = models.CharField(max_length=10, default="#000000")
    icon = models.CharField(max_length=30, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# FrequentAskedQuestion: model ...

class FrequentAskedQuestion(models.Model):
    """
    Frequent asked question model.
    Issue #6
    """

    # defines rendering order in template. Do not use IntegerField
    order = models.CharField("orden", max_length=3)
    question = models.CharField("Pregunta", max_length=200)
    answer = models.TextField("Respuesta", max_length=1000)

    active = models.BooleanField(default=True)

    class Meta:
        # table actual name
        db_table = "core_faq"

        # default "ORDER BY" statement
        ordering = ["order"]

    def __str__(self):
        return self.question

# HelpRequest: represents a ...

class HelpRequest(models.Model):
    title = models.CharField(
        _("Request title"),
        max_length=200,
        help_text=_("Short description of what you need"),
        db_index=True,
    )
    message = models.TextField(
        _("Request Description"),
        help_text=mark_safe(
            _("Here you can tell in detail what you need, <b> the better you tell your situation the more likely they want to help you </b>")),
        max_length=2000,
        null=True,
        db_index=True,
    )
    name = models.CharField(_("Name and surname"), max_length=200)
    phone = models.CharField(_("Telephone contact"), max_length=30)
    address = models.CharField(
        _("Address"),
        help_text=_("Your address, city, neighborhood, references, or how to get there, to get help"),
        max_length=400,
        blank=False,
        null=True,
    )
    location = models.PointField(
        _("Location"),
        # XXX Get rid of all HTML out of the model
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">{}<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
        _("Select your location so that people can find you, if you do not want to mark your home a good option may be the nearest police station or some other nearby public place."),
        _("If you have problems with this step"),
        _("Check out this help")
        )),
        srid=4326,
    )
    picture = models.ImageField(
        _("Photo"),
        upload_to=rename_img,
        help_text=_("In case you want you can attach a photo related to your request. It is optional but it can help people better understand your situation."),
        null=True,
        blank=True,
    )
    resolved = models.BooleanField(default=False, db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField(_("Added"), auto_now_add=True, null=True, blank=True, db_index=True)
    upvotes = models.IntegerField(default=0, blank=True)
    downvotes = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=50, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=50, blank=True, default="", editable=False)
    categories = models.ManyToManyField(Category, blank=True)
    search_vector = SearchVectorField()
    history = HistoricalRecords()
    objects = HelpRequestQuerySet.as_manager()

    @property
    def thumb(self):
        filepath, extension = path.splitext(self.picture.url)
        return f"{filepath}_th{extension}"

    def _get_city(self):
        geolocator = Nominatim(user_agent="ayudapy")
        cordstr = "%s, %s" % self.location.coords[::-1]
        city = ''
        try:
            location = geolocator.reverse(cordstr, language='es')
            if location.raw.get('address'):
                if location.raw['address'].get('city'):
                    city = location.raw['address']['city']
                elif location.raw['address'].get('town'):
                    city = location.raw['address']['town']
                elif location.raw['address'].get('locality'):
                    city = location.raw['address']['locality']
        except Exception as e:
            logger.error(f"Geolocator unavailable: {repr(e)}")
        return city

    def _deactivate_duplicates(self):
        return HelpRequest.objects.filter(phone=self.phone).update(active=False)

    def save(self, *args, **kwargs):
        from unidecode import unidecode
        city = self._get_city()
        self.city = city
        self.city_code = unidecode(city).replace(" ", "_")
        self.phone = self.phone.replace(" ", "")
        if not self.id:
            self._deactivate_duplicates()
        return super(HelpRequest, self).save(*args, **kwargs)

    def __str__(self):
        return f"<Pedido #{self.id} - {self.name}>"


@receiver(post_save, sender=HelpRequest)
def thumbnail(sender, instance, created, **kwargs):
    if instance.picture:
        try:
            create_thumbnail(
                settings.MEDIA_ROOT + str(instance.picture), THUMBNAIL_BASEWIDTH
            )
        except Exception as e:
            logger.error(f"Error creating thumbnail: {repr(e)}")


# Status: ...

class Status(models.Model):
    name = models.CharField(
        "Nombre del estado",
        max_length=40,
        help_text="Nombre del estado"
    )
    code = models.CharField(
        "Código del estado",
        max_length=10,
        help_text="Código del estado",
        primary_key=True,
    )
    active = models.BooleanField(default=True, db_index=True)


# Devices are going to be registered and identified by cookies (in browsers)
# or by any other thing

class Device(models.Model):
    device_iid = models.AutoField(
        primary_key=True
    )
    device_id = models.CharField(
        "Id Dispositivo",
        max_length=128,
        help_text="Identificador del Dispositivo",
        unique=True
    )
    ua_string = models.CharField(
        "User Agent",
        max_length=512,
        help_text="User Agent",
        null=True,
        blank=True
    )
    status = models.CharField(
        "Estado",
        max_length=32,
        help_text="Estado del Dispositivo",
        default="ACTIVE"
    )
    dev_brand = models.CharField(
        "Marca",
        max_length=128,
        help_text="Marca del Dispositivo",
        null=True,
        blank=True
    )
    dev_family = models.CharField(
        "Familia",
        max_length=128,
        help_text="Familia del Dispositivo",
        null=True,
        blank=True
    )
    dev_model = models.CharField(
        "Modelo",
        max_length=128,
        help_text="Modelo del Dispositivo",
        null=True,
        blank=True
    )
    os_family = models.CharField(
        "SO",
        max_length=128,
        help_text="Sistema Operativo",
        null=True,
        blank=True
    )
    os_version = models.CharField(
        "Version SO",
        max_length=32,
        help_text="Versión del Sistema Operativo",
        null=True,
        blank=True
    )
    browser_family = models.CharField(
        "Navegador",
        max_length=64,
        help_text="Navegador del User Agent",
        null=True,
        blank=True
    )
    browser_version = models.CharField(
        "Version Navegador",
        max_length=32,
        help_text="Versión del Navegador del User Agent",
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        "Creado",
        help_text="Fecha de Creación del Dispositivo",
        auto_now=True
    )
    last_seen = models.DateTimeField(
        "Última Visita",
        help_text="Última Visita del Dispositivo",
        auto_now_add=True
    )
    created_ip_address = models.CharField(
        "IP de creación",
        help_text="Dirección IP desde la que fue creado",
        max_length=32,
        null=True,
        blank=True
    )
    push_notification_token = models.CharField(
        "Token de Notificación",
        help_text="Token de Notificación para envíos tipo PUSH",
        max_length=128,
        null=True,
        blank=True
    )


# User: to represent a user in ayudapy

class User(models.Model):
    user_iid = models.AutoField(
        primary_key=True
    )
    user_type = models.CharField(
        "Tipo",
        max_length=32,
        help_text="Tipo de usuario"
    )
    user_value = models.CharField(
        "Sujeto",
        max_length=128,
        help_text="Valor/Nombre de Usuario"
    )
    name = models.CharField(
        "Nombre Completo",
        max_length=512,
        help_text="Nombre Completo del Usuario",
        null=True,
        blank=True
    )
    email = models.CharField(
        "Correo Electrónico",
        max_length=256,
        help_text="Correo Electrónico del Usuario",
        null=True,
        blank=True
    )
    phone = models.CharField(
        "Teléfono",
        max_length=64,
        help_text="Número Telefónico del Usuario",
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        "Creado",
        help_text="Fecha de Creación del Dispositivo",
        auto_now=True
    )
    last_seen = models.DateTimeField(
        "Última Visita",
        help_text="Última Visita del Dispositivo",
        auto_now_add=True
    )
    created_ip_address = models.CharField(
        "IP de creación",
        help_text="Dirección IP desde la que fue creado",
        max_length=32,
        null=True,
        blank=True
    )
    address = models.CharField(
        "Dirección",
        help_text="Dirección por defecto del Usuario",
        max_length=400,
        blank=True,
        null=True,
    )
    location = models.PointField(
        "Ubicación",
        help_text="Ubicación por defecto del Usuario",
        blank=True,
        null=True,
    )
    city = models.CharField(
        "Ciudad",
        max_length=30,
        help_text="Dirección por defecto del Usuario",
        blank=True,
        null=True
    )
    city_code = models.CharField(
        "Código Ciudad",
        max_length=50,
        help_text="Código de Ciudad por Defecto del Usuario",
        blank=True,
        null=True
    )
    password_hash = models.CharField(
        "Password",
        max_length=64,
        help_text="Contraseña del Usuario",
        blank=True,
        null=True
    )
    password_salt = models.CharField(
        "Password Salta",
        max_length=64,
        help_text="Salt de Contraseña del Usuario",
        blank=True,
        null=True
    )
    history = HistoricalRecords()


class HelpRequestOwner(models.Model):
    help_request = models.OneToOneField(
        HelpRequest,
        on_delete=models.CASCADE,
        primary_key=True
    )
    user_iid = models.ForeignKey(User, on_delete=models.CASCADE)
