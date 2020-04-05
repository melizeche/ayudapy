import logging
from os import path

from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import create_thumbnail, rename_img

logger = logging.getLogger(__name__)
THUMBNAIL_BASEWIDTH = 500


class HelpRequest(models.Model):
    title = models.CharField(
        "Título del pedido", max_length=200, help_text="Descripción corta de que estás necesitando"
    )
    message = models.TextField(
        "Descripción del pedido",
        help_text="Acá podes contar detalladamente lo que necesitas",
        max_length=2000,
        null=True,
        blank=True,
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
        help_text="Seleccioná tu ubicación para que la gente pueda encontrarte, si no querés marcar tu casa una buena opción puede ser la comisaria más cercana o algún otro sitio público cercano",
        srid=4326,
    )
    picture = models.ImageField(
        "Foto",
        upload_to=rename_img,
        help_text="Si querés podés adjuntar una foto relacionada con tu pedido, es opcional pero puede ayudar a que la gente entienda mejor tu situación",
        null=True,
        blank=True,
    )
    active = models.BooleanField(default=True)
    added = models.DateTimeField("Agregado", auto_now_add=True, null=True, blank=True)
    votsi = models.IntegerField(default=0, blank=True)
    votno = models.IntegerField(default=0, blank=True)

    @property
    def thumb(self):
        print("AAA!")
        filepath, extension = path.splitext(self.picture.url)
        return f"{filepath}_th{extension}"

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
