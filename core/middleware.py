# Silent (won't fail if there is an exception) middleware
# to get/create a device when processing a request in AyudaPY
import datetime
import uuid
import ua_parser

from core.models import User, Device

DEVICE_ID_COOKIE_NAME="ayudapydevid"
USER_TYPE_DEVICE="DEVICE_USER"


class AyudaPYMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    # will take care of device creation
    def __call__(self, request):

        request.ayuda_session = {
            "user": None,
            "device": None,
            "must_set_cookie": False
        }

        try:
            request.ayuda_session["device"] = self.get_or_create_device(request)
            request.ayuda_session["user"] = self.get_or_create_user(request, request.ayuda_session['device'])
        except Exception as e:
            # ignore if there is an error
            pass

        response = self.get_response(request)

        # setup cookie
        if request.ayuda_session['must_set_cookie'] and request.ayuda_session['device'] is not None:
            # cookie won't expire until year 2067
            dt = datetime.datetime(year=2067,month=12,day=31)
            response.set_cookie(DEVICE_ID_COOKIE_NAME, request.ayuda_session['device'].device_id, expires=dt)

        return response

    def get_device_if_exists(self, request):

        if DEVICE_ID_COOKIE_NAME not in request.COOKIES:
            return None

        device_id = request.COOKIES[DEVICE_ID_COOKIE_NAME]
        # checks if device is present in database
        try:
            return Device.objects.get(device_id=device_id)
        except Device.DoesNotExist as e:
            return None

    def get_version(self, x):
        v = ""
        if x.major is not None:
            v += x.major
        if x.minor is not None:
            v += "." + x.minor
        return v

    def do_create_device(self, request):

        ua_str = request.META.get('HTTP_USER_AGENT')
        # Raises TypeError when the request carries no User-Agent header, which
        # __call__ swallows: a device is only created for identifiable clients.
        # with_defaults() fills the parts ua_parser could not match with "Other".
        ua = ua_parser.parse(ua_str).with_defaults()

        device = Device()

        device.device_id = str(uuid.uuid4())

        device.dev_family = ua.device.family
        device.dev_brand = ua.device.brand
        device.dev_model = ua.device.model

        device.browser_family = ua.user_agent.family
        device.browser_version = self.get_version(ua.user_agent)

        device.os_family = ua.os.family
        device.os_version = self.get_version(ua.os)

        device.created_ip_address = request.META.get('REMOTE_ADDR')
        device.ua_string = ua_str

        device.save()

        return device

    def get_or_create_device(self, request):

        # check if device exists in database based on cookie value
        device = self.get_device_if_exists(request)

        # if device does not exist, create it
        if device is None:
            device = self.do_create_device(request)
            request.ayuda_session['must_set_cookie'] = True

        return device

    def do_create_user(self, request, device):
        u = User()
        u.created_ip_address = request.META.get('REMOTE_ADDR')
        u.user_type = USER_TYPE_DEVICE
        u.user_value = device.device_id
        u.save()
        return u

    def get_or_create_user(self, request, device):
        try:
            # check if user exists in database based on device id
            user = User.objects.get(user_type=USER_TYPE_DEVICE, user_value=device.device_id)
        except User.DoesNotExist as e:
            # user not found, create user
            user = self.do_create_user(request, device)

        return user
