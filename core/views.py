from django.contrib import messages
from django.core.serializers import serialize
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
    get_list_or_404,
)
from django.contrib.admin import SimpleListFilter
from .forms import HelpRequestForm
from .models import HelpRequest

# Create your views here.


def home(request):
    return render(request, "home.html")


def request_form(request):
    if request.method == "POST":
        form = HelpRequestForm(request.POST, request.FILES)
        if form.is_valid():
            new_help_request = form.save()
            messages.success(request, "Se creó tu pedido exitosamente!")
            return redirect("pedidos-detail", id=new_help_request.id)
    else:
        form = HelpRequestForm()
    return render(request, "help_request_form.html", {"form": form})


def view_request(request, id):
    help_request = get_object_or_404(HelpRequest, pk=id)
    context = {
        "help_request": help_request,
        "thumbnail": help_request.thumb if help_request.picture else None,
    }
    return render(request, "request.html", context)


def list_requests(request):
    list_help_requests = HelpRequest.objects.filter(active=True).order_by("-added")  # TODO limit this
    query = list_help_requests[:200]
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))
    context = {"list_help": list_help_requests, "geo": geo}
    return render(request, "list.html", context)


def list_by_city(request, city):
    list_help_requests = HelpRequest.objects.filter(city_code=city).order_by("-added")  # TODO limit this
    query = list_help_requests[:200]
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))
    context = {"list_help": list_help_requests, "geo": geo}
    return render(request, "list_by_city.html", context)
