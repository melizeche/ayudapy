from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)
# from django.contrib.auth.decorators import login_required

from .forms import DonationForm
from .models import DonationCenter
from core.utils import text_to_image, image_to_base64

from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from django.views.generic import TemplateView


@method_decorator(permission_required("org.add_donationcenter"), name="dispatch")
class RestrictedView(TemplateView):
    template_name = "donation_center/info.html"


@permission_required('org.add_donationcenter')
def donation_form(request):
    if request.method == "POST":
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            new_donation = form.save()

            messages.success(request, "¡Tu donación se agregó exitosamente!")
            return redirect("donaciones-detail", id=new_donation.id)
    else:
        form = DonationForm()
    return render(request, "donation_center/create.html", {"form": form})


def view_donation_center(request, id):
    donation_center = get_object_or_404(DonationCenter, pk=id)

    context = {
        "donation_center": donation_center,
        "name": donation_center.name,
        "phone_number_img": image_to_base64(text_to_image(donation_center.phone, 300, 50)) if donation_center.phone else None,
        "whatsapp": '595'+donation_center.phone[1:]+'?text=Hola+'+donation_center.name
                    + ',+te+escribo+por+el+anuncio+de+donación+que+hiciste:+'
                    + '+https:'+'/'+'/'+'ayudapy.org/donaciones/'+donation_center.id.__str__() if donation_center.phone else None,
    }

    return render(request, "donation_center/details.html", context)


# Create your views here.
def list_donation(request):
    cities = [(i['city'], i['city_code']) for i in DonationCenter.objects.all(
    ).values('city', 'city_code').distinct('city_code').order_by('city_code')]
    context = {"list_donation_cities": cities}
    return render(request, "donation_center/list.html", context)


def list_donation_by_city(request, city):
    list_donations = DonationCenter.objects.filter(city_code=city).order_by("-added")  # TODO limit this
    city = list_donations[0].city
    query = list_donations
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))

    page = request.GET.get('page', 1)
    paginate_by = 25
    paginator = Paginator(list_donations, paginate_by)
    try:
        list_paginated = paginator.page(page)
    except PageNotAnInteger:
        list_paginated = paginator.page(1)
    except EmptyPage:
        list_paginated = paginator.page(paginator.num_pages)

    context = {"list_donations": list_donations, "geo": geo, "city": city, "list_paginated": list_paginated}
    return render(request, "donation_center/list_by_city.html", context)
