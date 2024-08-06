from vendors.models import Vendor

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