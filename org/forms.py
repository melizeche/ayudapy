from django import forms
from leaflet.forms.widgets import LeafletWidget
from django.core.exceptions import NON_FIELD_ERRORS

from .models import DonationCenter

class DonationForm(forms.ModelForm):
    class Meta:
        model = DonationCenter
        fields = (
            "name",
            "phone",
            "location",
            "address",
        )
        widgets = {
            "location": LeafletWidget(),
            "name": forms.TextInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Registro ya ingresado, no puede duplicar mismo pedido.",
            }
        }
