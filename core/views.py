from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)
from rest_framework import viewsets
from rest_framework import filters
from rest_framework_gis.filters import InBBoxFilter
from django_filters.rest_framework import DjangoFilterBackend

from .forms import HelpRequestForm
from .models import HelpRequest, FrequentAskedQuestion
from .serializers import HelpRequestSerializer, HelpRequestGeoJSONSerializer
from .utils import text_to_image, image_to_base64


class HelpRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HelpRequest.objects.filter(active=True)
    serializer_class = HelpRequestSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'phone',]
    filterset_fields = ['city']
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True


class HelpRequestGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HelpRequest.objects.filter(active=True)
    pagination_class = None
    serializer_class = HelpRequestGeoJSONSerializer
    bbox_filter_field = 'location'
    filter_backends = (InBBoxFilter, )
    bbox_filter_include_overlapping = True


def home(request):
    return render(request, "home.html")


def request_form(request):
    if request.method == "POST":
        form = HelpRequestForm(request.POST, request.FILES)
        if form.is_valid():
            new_help_request = form.save()
            messages.success(request, "¡Se creó tu pedido exitosamente!")
            return redirect("pedidos-detail", id=new_help_request.id)
    else:
        form = HelpRequestForm()
    return render(request, "help_request_form.html", {"form": form})


def view_request(request, id):
    help_request = get_object_or_404(HelpRequest, pk=id)
    context = {
        "help_request": help_request,
        "thumbnail": help_request.thumb if help_request.picture else "/static/favicon.ico",
        "phone_number_img": image_to_base64(text_to_image(help_request.phone, 300, 50))
    }
    if request.POST:
        if request.POST['vote']:
            if request.POST['vote'] == 'up':
                help_request.upvotes += 1
            elif request.POST['vote'] == 'down':
                help_request.downvotes += 1
            help_request.save()
    return render(request, "request.html", context)


def view_faq(request):
    """ Frequent Asked Questions controller """
    try:
        faq_list = FrequentAskedQuestion.objects.filter(active=True)
    except:
        # no exception should break the flow.
        faq_list = []

    context = {
        'faq_list': faq_list
    }

    template = "general_faq.html"

    return render(request, template, context)


def list_requests(request):
    list_help_requests = HelpRequest.objects.filter(active=True).order_by("-added")  # TODO limit this
    cities = [(i['city'], i['city_code']) for i in HelpRequest.objects.all().values('city', 'city_code').distinct().order_by('city_code')]
    query = list_help_requests
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))

    # Start Pagination
    page = request.GET.get('page', 1)
    paginate_by = 25
    paginator = Paginator(list_help_requests, paginate_by)

    try:
        list_help_requests_paginated = paginator.page(page)
    except PageNotAnInteger:
        list_help_requests_paginated = paginator.page(1)
    except EmptyPage:
        list_help_requests_paginated = paginator.page(paginator.num_pages)
    # End Pagination

    context = {"list_cities": cities, "list_help": list_help_requests, "geo": geo, "list_help_paginated": list_help_requests_paginated}
    return render(request, "list.html", context)


def list_by_city(request, city):
    list_help_requests = HelpRequest.objects.filter(city_code=city).order_by("-added")  # TODO limit this
    city = list_help_requests[0].city
    query = list_help_requests
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))

    page= request.GET.get('page', 1)
    paginate_by = 25
    paginator = Paginator(list_help_requests,paginate_by)
    try:
        list_help_requests_paginated = paginator.page(page)
    except PageNotAnInteger:
        list_help_requests_paginated = paginator.page(1)
    except EmptyPage:
        list_help_requests_paginated = paginator.page(paginator.num_pages)

    context = {"list_help": list_help_requests, "geo": geo, "city": city, "list_help_paginated": list_help_requests_paginated}
    return render(request, "list_by_city.html", context)
