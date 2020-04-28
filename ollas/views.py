from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from django.shortcuts import (
    redirect,
    render,
    get_object_or_404,
)

from urllib.parse import quote_plus
import json
import datetime
import base64

from .models import OllaPopular, OllaPopularOwner
from .forms import OllaPopularForm

from core.utils import text_to_image, image_to_base64

# Create your views here.
def set_owner_and_update_values(request, new_help_request):
    if 'user' in request.ayuda_session and request.ayuda_session['user'] is not None:
        user = request.ayuda_session['user']
        olla_popular_owner = OllaPopularOwner()
        olla_popular_owner.olla_popular = new_help_request
        olla_popular_owner.user_iid = user
        olla_popular_owner.save()

        # try to update user values
        if user.name is None:
            user.name = olla_popular_owner.help_request.name
            user.city = olla_popular_owner.help_request.city
            user.city_code = olla_popular_owner.help_request.city_code
            user.phone = olla_popular_owner.help_request.phone
            user.address = olla_popular_owner.help_request.address
            user.location = olla_popular_owner.help_request.location
            user.save()

def olla_form(request):
    if request.method == "POST":
        form = OllaPopularForm(request.POST, request.FILES)
        if form.is_valid():
            new_olla_popular = form.save()
            try:
                set_owner_and_update_values(request, new_olla_popular)
            except Exception as e:
                # ignore if we can't set the help_request_ownser
                print(str(e))

            messages.success(request, "¡Se creó tu olla popular exitosamente!")
            return redirect("olla-detail", id=new_olla_popular.id)
    else:
        form = OllaPopularForm()
    return render(request, "olla_popular/create.html", {"form": form})


def view_olla(request, id):
    olla_popular = get_object_or_404(OllaPopular, pk=id)
    active_ollas = []
    if not olla_popular.active:
        active_ollas = OllaPopular.objects.filter(phone=olla_popular.phone, active=True).order_by('-pk')
    vote_ctrl = {}
    vote_ctrl_cookie_key = 'votectrl'
    # cookie expiration
    dt = datetime.datetime(year=2067, month=12, day=31)

    context = {
        "olla_popular": olla_popular,
        "name": olla_popular.name,
        "thumbnail": olla_popular.thumb if olla_popular.picture else "/static/img/logo.jpg",
        "phone_number_img": image_to_base64(text_to_image(olla_popular.phone, 300, 50)),
        "whatsapp": '595'+olla_popular.phone[1:]+'?text=Hola+'+olla_popular.name
                    + ',+te+escribo+por+la+olla+popular+que+creaste:+'+quote_plus(olla_popular.title)
                    + '+https:'+'/'+'/'+'ayudapy.org/ollas/'+olla_popular.id.__str__(),
        "active_ollas": active_ollas,
    }
    if request.POST:
        if request.POST['vote']:
            if vote_ctrl_cookie_key in request.COOKIES:
                try:
                    vote_ctrl = json.loads(base64.b64decode(request.COOKIES[vote_ctrl_cookie_key]))
                except:
                    pass

                try:
                    voteFlag = vote_ctrl["{id}".format(id=olla_popular.id)]
                except KeyError:
                    voteFlag = None

                if voteFlag is None:
                    if request.POST['vote'] == 'up':
                        olla_popular.upvotes += 1
                    elif request.POST['vote'] == 'down':
                        olla_popular.downvotes += 1
                    olla_popular.save()
                    vote_ctrl["{id}".format(id=olla_popular.id)] = True

    response = render(request, "olla_popular/details.html", context)

    if vote_ctrl_cookie_key not in request.COOKIES:
        # initialize control cookie
        if request.POST and request.POST['vote']:
            # set value in POST request if cookie not exists
            b = json.dumps({"{id}".format(id=olla_popular.id): True}).encode('utf-8')
        else:
            # set empty value in others requests
            b = json.dumps({}).encode('utf-8')
        value = base64.b64encode(b).decode('utf-8')
        response.set_cookie(vote_ctrl_cookie_key, value,
                            expires=dt)
    else:
        if request.POST:
            if request.POST['vote']:
                # update control cookie only in POST request
                b = json.dumps(vote_ctrl).encode('utf-8')
                value = base64.b64encode(b).decode('utf-8')
                response.set_cookie(vote_ctrl_cookie_key, value,
                                    expires=dt)
    return response


def list_ollas(request):
    cities = [(i['city'], i['city_code']) for i in OllaPopular.objects.all().values('city', 'city_code').distinct().order_by('city_code')]
    context = {"list_cities": cities}
    return render(request, "olla_popular/list.html", context)


def list_by_city(request, city):
    list_ollas_populares = OllaPopular.objects.filter(city_code=city, active=True, resolved=False).order_by("-added")  # TODO limit this
    city = list_ollas_populares[0].city
    query = list_ollas_populares
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))

    page = request.GET.get('page', 1)
    paginate_by = 25
    paginator = Paginator(list_ollas_populares, paginate_by)
    try:
        list_paginated = paginator.page(page)
    except PageNotAnInteger:
        list_paginated = paginator.page(1)
    except EmptyPage:
        list_paginated = paginator.page(paginator.num_pages)

    context = {"list_ollas": list_ollas_populares, "geo": geo, "city": city, "list_paginated": list_paginated}
    return render(request, "olla_popular/list_by_city.html", context)
