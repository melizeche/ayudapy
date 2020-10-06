from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

from geopy.geocoders import Nominatim

DEP = (
    (0, "Asuncion"),
    (1, "Alto Paraguay"),
    (2, "Alto Paraná"),
    (3, "Amambay"),
    (4, "Boquerón"),
    (5, "Caaguazú"),
    (6, "Caazapá"),
    (7, "Canindeyú"),
    (8, "Central"),
    (9, "Concepción"),
    (10, "Cordillera"),
    (11, "Guairá"),
    (12, "Itapúa"),
    (13, "Misiones"),
    (14, "Ñeembucú"),
    (15, "Paraguarí"),
    (16, "Presidente Hayes"),
    (17, "San Pedro"),
)


class BaseResource(models.Model):
    location = models.PointField("Ubicación", srid=4326,)
    address = models.CharField(
        "Dirección",
        help_text="Dirección, ciudad, barrio, referencias, o cómo llegar",
        max_length=400,
        blank=False,
        null=True,
    )
    city = models.CharField(max_length=30, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=30, blank=True, default="", editable=False)
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField(
        "Agregado", auto_now_add=True, null=True, blank=True, db_index=True
    )
    history = HistoricalRecords(inherit=True)

    def _get_city(self):
        geolocator = Nominatim(user_agent="ayudapy")
        cordstr = "%s, %s" % self.location.coords[::-1]
        location = geolocator.reverse(cordstr, language="es")
        city = ""
        if location.raw.get("address"):
            if location.raw["address"].get("city"):
                city = location.raw["address"]["city"]
            elif location.raw["address"].get("town"):
                city = location.raw["address"]["town"]
            elif location.raw["address"].get("locality"):
                city = location.raw["address"]["locality"]
        return city

    def save(self):
        from unidecode import unidecode
        city = self._get_city()
        self.city = city
        self.city_code = unidecode(city).replace(" ", "_")
        self.phone = self.phone.replace(" ", "")
        return super().save()

    class Meta:
        abstract = True


# Organization represents ...


class Organization(models.Model):
    name = models.CharField("Nombre de la Organización", max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Organización"
        verbose_name = "Organizaciones"

# Donation Center represents an establishment where the user with needs could go to
# receive some help.


class DonationCenter(models.Model):
    name = models.CharField("Nombre del lugar", max_length=200)
    phone = models.CharField("Teléfono de contacto", max_length=30, blank=True, null=True)
    location = models.PointField("Ubicación", srid=4326,)
    address = models.CharField(
        "Dirección",
        help_text="Dirección, ciudad, barrio, referencias, o cómo llegar",
        max_length=400,
        blank=False,
        null=True,
    )
    city = models.CharField(max_length=30, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=30, blank=True, default="", editable=False)
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField(
        "Agregado", auto_now_add=True, null=True, blank=True, db_index=True
    )
    history = HistoricalRecords()

    # TODO - getCity() se utliza en HelpRequest y otros modelos. Se podria unificar
    def _get_city(self):
        geolocator = Nominatim(user_agent="ayudapy")
        cordstr = "%s, %s" % self.location.coords[::-1]
        location = geolocator.reverse(cordstr, language="es")
        city = ""
        if location.raw.get("address"):
            if location.raw["address"].get("city"):
                city = location.raw["address"]["city"]
            elif location.raw["address"].get("town"):
                city = location.raw["address"]["town"]
            elif location.raw["address"].get("locality"):
                city = location.raw["address"]["locality"]
        return city

    def save(self):
        from unidecode import unidecode

        city = self._get_city()
        self.city = city
        self.city_code = unidecode(city).replace(" ", "_")
        self.phone = self.phone.replace(" ", "")
        return super(DonationCenter, self).save()

    def __str__(self):
        return f"<Centro #{self.id} - {self.name}> - {self.city}"

    class Meta:
        verbose_name = "Centro de Donación"
        verbose_name_plural = "Centros de Donación"


# Profile a model to represents volunteers.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField("Nombre", max_length=200)
    phone = models.CharField("Teléfono de contacto", max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    location = models.PointField("Ubicación", srid=4326,)
    department = models.PositiveSmallIntegerField(choices=DEP)
    address = models.CharField(
        "Dirección",
        help_text="Dirección, ciudad, barrio, referencias, o cómo llegar",
        max_length=400,
        blank=False,
        null=True,
    )
    city = models.CharField(max_length=30, blank=True, default="", editable=False)
    city_code = models.CharField(max_length=30, blank=True, default="", editable=False)
    active = models.BooleanField(default=True, db_index=True)
    added = models.DateTimeField(
        "Agregado", auto_now_add=True, null=True, blank=True, db_index=True
    )

    def _get_city(self):
        geolocator = Nominatim(user_agent="ayudapy")
        cordstr = "%s, %s" % self.location.coords[::-1]
        location = geolocator.reverse(cordstr, language="es")
        city = ""
        if location.raw.get("address"):
            if location.raw["address"].get("city"):
                city = location.raw["address"]["city"]
            elif location.raw["address"].get("town"):
                city = location.raw["address"]["town"]
            elif location.raw["address"].get("locality"):
                city = location.raw["address"]["locality"]
        return city

    def save(self, **kwargs):
        from unidecode import unidecode

        city = self._get_city()
        self.city = city
        self.city_code = unidecode(city).replace(" ", "_")
        return super(Profile, self).save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Voluntario"


class Pool(BaseResource):
    name = models.CharField("Nombre y Apellido", max_length=200, help_text="Nombre de la persona encargada")
    phone = models.CharField("Teléfono de contacto", max_length=30)
    info = models.TextField("Información", help_text="Cantidad de litros o dimensiones, ¿es una piscina o un reservorio?, etc...", blank=True, null=True)

    def __str__(self):
        return f"<Piscina #{self.id} - {self.name}> - {self.city}"
