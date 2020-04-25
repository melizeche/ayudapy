from django import forms
from leaflet.forms.fields import PointField
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe

from .models import OllaPopular


class OllaPopularForm(forms.ModelForm):
    location = PointField(
        label="Ubicación",
        error_messages={'required': mark_safe('Te olvidaste de marcar tu ubicación en el mapita\n <br>Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">mirá esta ayuda</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>')},
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">Seleccioná tu ubicación para que la gente pueda encontrarte, si no querés marcar tu casa una buena opción puede ser la comisaría más cercana o algún otro sitio público cercano.\
            <br>Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">mirá esta ayuda</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'),
        )

    class Meta:
        model = OllaPopular
        fields = (
            "title",
            "message",
            "name",
            "phone",
            "location",
            "address",
            "picture"
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Ejemplo: Olla Popular del barrio Caacupemi del Bañado Sur",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "rows": 4,
                    "placeholder": "Ejemplo: Somos un grupo de mujeres que nos organizamos para dar de comer a más de 220 personas, entre niños/as y adultos/as. Necesitamos alimentos para seguir dando de comer a nuestra gente: frutas, verduras, poroto, maiz, arroz, harina, aceite, carne, huevo... cualquier cosa ayuda.\nMuchas Gracias!",
                }
            ),
            "name": forms.TextInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Registro ya ingresado, no puede duplicar la misma olla popular.",
            }
        }
