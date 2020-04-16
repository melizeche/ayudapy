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

from .forms import HelpRequestForm
from .models import HelpRequest, HelpRequestOwner, FrequentAskedQuestion
from .utils import text_to_image, image_to_base64


def home(request):
    return render(request, "home.html")


def set_owner_and_update_values(request, new_help_request):
    if 'user' in request.ayuda_session and request.ayuda_session['user'] is not None:
        user = request.ayuda_session['user']
        help_request_owner = HelpRequestOwner()
        help_request_owner.help_request = new_help_request
        help_request_owner.user_iid = user
        help_request_owner.save()

        # try to update user values
        if user.name is None:
            user.name = help_request_owner.help_request.name
            user.city = help_request_owner.help_request.city
            user.city_code = help_request_owner.help_request.city_code
            user.phone = help_request_owner.help_request.phone
            user.address = help_request_owner.help_request.address
            user.location = help_request_owner.help_request.location
            user.save()

def request_form(request):
    if request.method == "POST":
        form = HelpRequestForm(request.POST, request.FILES)
        if form.is_valid():
            new_help_request = form.save()
            try:
                set_owner_and_update_values(request, new_help_request)
            except Exception as e:
                # ignore if we can't set the help_request_ownser
                print(str(e))

            messages.success(request, "¡Se creó tu pedido exitosamente!")
            return redirect("pedidos-detail", id=new_help_request.id)
    else:
        form = HelpRequestForm()
    return render(request, "help_request_form.html", {"form": form})


def view_request(request, id):
    help_request = get_object_or_404(HelpRequest, pk=id)
    vote_ctrl = {}
    vote_ctrl_cookie_key = 'votectrl'
    # cookie expiration 
    dt = datetime.datetime(year=2067,month=12,day=31)

    context = {
        "help_request": help_request,
        "thumbnail": help_request.thumb if help_request.picture else "/static/favicon.ico",
        "phone_number_img": image_to_base64(text_to_image(help_request.phone, 300, 50)),
        "whatsapp": '595'+help_request.phone[1:]+'?text=Hola+'+help_request.name
                    +',+te+escribo+por+el+pedido+que+hiciste:+'+quote_plus(help_request.title)
                    +'+https:'+'/'+'/'+'ayudapy.org/pedidos/'+help_request.id.__str__()
    }
    if request.POST:
        if request.POST['vote']:
            if vote_ctrl_cookie_key in request.COOKIES:
                try:
                    vote_ctrl = json.loads(base64.b64decode(request.COOKIES[vote_ctrl_cookie_key]))
                except:
                    pass 

                try:
                    voteFlag = vote_ctrl["{id}".format(id=help_request.id)]
                except KeyError:
                    voteFlag = None

                if voteFlag is None:
                    if request.POST['vote'] == 'up':
                        help_request.upvotes += 1
                    elif request.POST['vote'] == 'down':
                        help_request.downvotes += 1
                    help_request.save()
                    vote_ctrl["{id}".format(id=help_request.id)] = True                    

    response = render(request, "request.html", context)

    if vote_ctrl_cookie_key not in request.COOKIES:
        # initialize control cookie
        if request.POST and request.POST['vote']:
            # set value in POST request if cookie not exists 
            b = json.dumps({"{id}".format(id=help_request.id): True}).encode('utf-8')
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
    cities = [(i['city'], i['city_code']) for i in HelpRequest.objects.all().values('city', 'city_code').distinct().order_by('city_code')]
    context = {"list_cities": cities}
    return render(request, "list.html", context)


def list_by_city(request, city):
    list_help_requests = HelpRequest.objects.filter(city_code=city).order_by("-added")  # TODO limit this
    city = list_help_requests[0].city
    query = list_help_requests
    geo = serialize("geojson", query, geometry_field="location", fields=("name", "pk", "title", "added"))

    page= request.GET.get('page', 1)
    paginate_by = 25
    paginator = Paginator(list_help_requests, paginate_by)
    try:
        list_paginated = paginator.page(page)
    except PageNotAnInteger:
        list_paginated = paginator.page(1)
    except EmptyPage:
        list_paginated = paginator.page(paginator.num_pages)

    context = {"list_help": list_help_requests, "geo": geo, "city": city, "list_paginated": list_paginated}
    return render(request, "list_by_city.html", context)
