import logging
from os import path

from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from geopy.geocoders import Nominatim
from django.http import HttpResponseRedirect

from core.utils import create_thumbnail, rename_img

logger = logging.getLogger(__name__)
THUMBNAIL_BASEWIDTH = 500


class HelpRequest(models.Model):
    title = models.CharField(
        "Título del pedido",
        max_length=200,
        help_text="Descripción corta de que estás necesitando",
        db_index=True,
    )
    message = models.TextField(
        "Descripción del pedido",
        help_text=mark_safe("Acá podes contar detalladamente lo que necesitas, <b>cuanto mejor cuentes tu situación es más probable que te quieran ayudar</b>"),
        max_length=2000,
        null=True,
        db_index=True,
    )
    name = models.CharField("Nombre y Apellido", max_length=200)
    phone = models.CharField("Teléfono de contacto", max_length=30)
    address = models.CharField(
        "Dirección",
        help_text="Es opcional pero puede ayudar a quien quiera ayudarte saber la direccion, ciudad, barrio, referencias, o como llegar",
        max_length=400,
        null=True,
        blank=True,
    )
    location = models.PointField(
        "Ubicación",
        help_text=mark_safe('Seleccioná tu ubicación para que la gente pueda encontrarte, si no querés marcar tu casa una buena opción puede ser la comisaría más cercana o algún otro sitio público cercano.\
            <br>Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">mirá esta ayuda</a>'),
        srid=4326,
    )
    picture = models.ImageField(
        "Foto",
        upload_to=rename_img,
        help_text="Si querés podés adjuntar una foto relacionada con tu pedido, es opcional pero puede ayudar a que la gente entienda mejor tu situación",
        null=True,
        blank=True,
    )
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField("Agregado", auto_now_add=True, null=True, blank=True, db_index=True)
    city = models.CharField(max_length=30, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=30, blank=True, default="", editable=False)
    country = models.CharField(max_length=30, default="", editable=False)
    country_code = models.CharField(max_length=30, default="", editable=False)
    votsi = models.IntegerField(default=0, blank=True)
    votno = models.IntegerField(default=0, blank=True)
    loc_validated = models.BooleanField(default=False)

    @property
    def thumb(self):
        filepath, extension = path.splitext(self.picture.url)
        return f"{filepath}_th{extension}"


    def _get_city(self, location):
        city = ''
        if location.raw.get('address'):
            if location.raw['address'].get('city'):
                city = location.raw['address']['city']
            elif location.raw['address'].get('town'):
                city = location.raw['address']['town']
            elif location.raw['address'].get('locality'):
                city = location.raw['address']['locality']
        return city


    def _get_country(self, location):
        country = ''
        if location.raw.get('address'):
            if location.raw['address'].get('country'):
                country = location.raw['address']['country']
        return country

    def _validate_loc(self):
        geolocator = Nominatim(user_agent="ayudapy")
        cordstr = "%s, %s" % self.location.coords[::-1]
        location = geolocator.reverse(cordstr, language='es')
        try:
            location.raw['address']
            return location
        except KeyError:
            return None

    def save(self):
        from unidecode import unidecode
        loc = self._validate_loc()
        if loc:
            city = self._get_city(loc)
            self.city = city
            self.city_code = unidecode(city).replace(" ", "_")
            country = self._get_country(loc)
            self.country = country
            self.country_code = unidecode(country).replace(" ", "_")
            self.loc_validated = True
        else:
            self.loc_validated = False
        return super(HelpRequest, self).save()

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
