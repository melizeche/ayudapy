from django.apps import AppConfig
from .models import HelpRequest


class CoreConfig(AppConfig):
    name = 'core'


def update_requests():
    for obj in HelpRequest.objects.all():
        obj.save()
