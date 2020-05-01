from django import forms
from leaflet.forms.fields import PointField
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .models import HelpRequest


class HelpRequestForm(forms.ModelForm):
    location = PointField(
        label="Ubicación",
        # XXX Move all HTML to the corresponding templates
        error_messages={'required': mark_safe('{}\n<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("You forgot to mark your location on the map"),
            _("If you have problems with this step"),
            _("Check out this help"),
            ))},
        help_text=mark_safe('<p style="margin-bottom:5px;font-size:10px;">{}.<br>{} <a href="#" class="is-link modal-button" data-target="#myModal" aria-haspopup="true">{}</a></p><p id="div_direccion" style="font-size: 10px; margin-bottom: 5px;"></p>'.format(
            _("Select your location so that people can find you, if you do not want to mark your home a good option may be the nearest police station or some other nearby public place."),
            _("If you have problems with this step"),
            _("Check out this help"),
            )),
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
                    "placeholder": _("Example: I urgently need food for my family"),
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "rows": 4,
                    "placeholder": _("Example: Due to the current situation I am in need of masks and cleaning products, any help, even a minimal one, will help me. Thank you so much!"),
                }
            ),
            "name": forms.TextInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
            'categories': forms.SelectMultiple(attrs={"style": "display:none;"}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _("Registration already entered, cannot duplicate the same request."),
            }
        }
