from django import forms
from leaflet.forms.widgets import LeafletWidget

from .models import HelpRequest


class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = (
            "title",
            "message",
            "name",
            "phone",
            "location",
            "address",
            "picture",
        )
        widgets = {
            "location": LeafletWidget(),
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
                    "placeholder": "Acá si podes detallar mejor lo que necesitas",
                }
            ),
            "name": forms.TextInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input", "type": "tel"}),
            "address": forms.TextInput(attrs={"class": "input"}),
        }
