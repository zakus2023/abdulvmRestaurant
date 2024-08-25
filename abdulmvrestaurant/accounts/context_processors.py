from vendors.models import Vendor
from django.conf import settings
from accounts.models import UserProfile

#use this function to get the vendor information
# #get the vendor who is signed in by filtering where user = request.user
# vendor = Vendor.objects.get(user=request.user)
# #pass the vendor as context dictionary so that it is available in the vendordashboard template
def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)

def get_user_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)



# for google api request
def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}

def get_paypal_client_id(request):
    return {'PAY_PAL_CLIENT_ID': settings.PAY_PAL_CLIENT_ID}
