from django import forms
from leaflet.forms.fields import PointField
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe

from .models import HelpRequest


class HelpRequestForm(forms.ModelForm):
    location = PointField(
        label="Ubicación",
        error_messages={'required': mark_safe('Te olvidaste de marcar tu ubicación en el mapita\n <br>Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">mirá esta ayuda</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>')},
        help_text=mark_safe('<p class="help text-muted has-text-left" style="margin:0 0 5px 5px;">Seleccioná tu ubicación para que la gente pueda encontrarte, si no querés marcar tu casa una buena opción puede ser la comisaría más cercana o algún otro sitio público cercano.</p> <p class="help text-muted has-text-left"><i class="fas fa-info-circle" style="font-size: 20px;margin-left: 5px; color: #2979ff;"></i>&nbsp;&nbsp;Si tenés problemas con este paso <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true" style="margin: 0 0 30px 0;">mirá esta ayuda</a></p><p id="div_direccion" style="font-size: 10px; margin:0 0 10px 0;"></p>'),
		)

    class Meta:
        model = HelpRequest
        fields = (
            "title",
            "message",
            "categories",
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
                    "placeholder": "Ejemplo: Necesito de manera urgente víveres para mi familia",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "rows": 4,
                    "placeholder": "Ejemplo: Por la situación actual estoy necesitando tapabocas y productos de limpieza, \
                        cualquier ayuda aunque sea mínima ya me va a ayudar.\nMuchas Gracias!",
                }
            ),
            "name": forms.TextInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            'categories': forms.SelectMultiple(attrs={"style": "display:none;"}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Registro ya ingresado, no puede duplicar mismo pedido.",
            }
        }
