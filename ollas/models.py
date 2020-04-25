import logging
from os import path

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.search import SearchVectorField, SearchQuery, SearchRank
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from geopy.geocoders import Nominatim
from simple_history.models import HistoricalRecords

from core.utils import create_thumbnail, rename_img
from core.models import User

logger = logging.getLogger(__name__)
THUMBNAIL_BASEWIDTH = 500

# Create your models here.
class OllaPopular(models.Model):
    title = models.CharField(
        "Nombre de la olla popular",
        max_length=200,
        help_text="Escribe un nombre para identificar a la Olla Popular",
        db_index=True,
    )
    message = models.TextField(
        "Descripción del la Olla Popular",
        help_text=mark_safe(
            "Acá podés contar detalladamente lo que necesitás para tu olla popular, <b>cuanto mejor cuentes tu situación es más probable que te quieran ayudar</b>"),
        max_length=2000,
        null=True,
        db_index=True,
    )
    name = models.CharField("Nombre y Apellido de el/la responsable", max_length=200)
    phone = models.CharField("Teléfono de contacto", max_length=30)
    address = models.CharField(
        "Dirección",
        help_text="Para ayudar a quien quiera ayudarte saber la dirección, ciudad, barrio, referencias, o cómo llegar",
        max_length=400,
        blank=False,
        null=True,
    )
    location = models.PointField(
        "Ubicación",
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">Seleccioná tu ubicación para que la gente pueda encontrarte, si no querés marcar tu casa una buena opción puede ser la comisaría más cercana o algún otro sitio público cercano.\
            <br>Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">mirá esta ayuda</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'),
        srid=4326,
    )
    picture = models.ImageField(
        "Foto",
        upload_to=rename_img,
        help_text="Si querés podés adjuntar una foto relacionada con tu olla popular, es opcional pero puede ayudar a que la gente entienda mejor tu situación",
        null=True,
        blank=True,
    )
    resolved = models.BooleanField(default=False, db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField("Agregado", auto_now_add=True, null=True, blank=True, db_index=True)
    upvotes = models.IntegerField(default=0, blank=True)
    downvotes = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=50, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=50, blank=True, default="", editable=False)
    # categories = models.ManyToManyField(Category, blank=True)
    search_vector = SearchVectorField()
    history = HistoricalRecords()
    # objects = HelpRequestQuerySet.as_manager()

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
        return OllaPopular.objects.filter(phone=self.phone).update(active=False)

    def save(self, *args, **kwargs):
        from unidecode import unidecode
        city = self._get_city()
        self.city = city
        self.city_code = unidecode(city).replace(" ", "_")
        self.phone = self.phone.replace(" ", "")
        if not self.id:
            self._deactivate_duplicates()
        return super(OllaPopular, self).save(*args, **kwargs)

    def __str__(self):
        return f"<Olla Popular #{self.id} - {self.title}>"

@receiver(post_save, sender=OllaPopular)
def thumbnail(sender, instance, created, **kwargs):
    if instance.picture:
        try:
            create_thumbnail(
                settings.MEDIA_ROOT + str(instance.picture), THUMBNAIL_BASEWIDTH
            )
        except Exception as e:
            logger.error(f"Error creating thumbnail: {repr(e)}")

class OllaPopularOwner(models.Model):
    olla_popular = models.OneToOneField(
        OllaPopular,
        on_delete=models.CASCADE,
        primary_key=True
    )
    user_iid = models.ForeignKey(User, on_delete=models.CASCADE)
