from django.shortcuts import render
from django.http import HttpResponse
from vendors.models import Vendor

# imports to create the point
from django.contrib.gis.geos import GEOSGeometry
# D is the shortcut for distance
from django.contrib.gis.measure import D 
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q


# helper function
def get_or_set_current_location_on_page_load(request):
    #  check if there is lat in the session 
     if 'lat' in request.session:
        #   assign the values of lat and lng to lat and lng 
          lat = request.session['lat']
          lng = request.session['lng']

         # return lat and lng 
          return lng, lat
     
    #  check if there is lat in the url query string or check if the user has clicked on the button to send the values there in the url
     elif 'lat' in request.GET:
        #   assign the values of lat and lng to lat and lng 
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        # store the the values of lat and lng in the session
        request.session['lat'] = lat
        request.session['lng'] = lng
        # return lat and lng
        return lng, lat
     else: return None        
          
     

def home(request):
    # this was added after implementing the PostGIS and GDAL-------------------------------
    # check if there is lat in the url query string
    # if 'lat' in request.GET:
    #     # get the value of lat and lng and store them in the variables lat and lng
    #     lat = request.GET.get('lat')
    #     lng = request.GET.get('lng')

    # i changed to this after writing the helper function on top. def get_or_set_...
    if get_or_set_current_location_on_page_load(request) is not None:
        # get the value of lat and lng and store them in the variables lat and lng
        # initially
        # ------------------------------------
        # lat = request.GET.get('lat')
        # lng = request.GET.get('lng')

        # pnt = GEOSGeometry('POINT(%s  %s)' %(lng, lat))
        # -----------------------------------------------
        # changed to. the fucntion returns lng,lat. so in place of request is lng, lat
        pnt = GEOSGeometry('POINT(%s  %s)' %(get_or_set_current_location_on_page_load(request)))


            
            # filter the vendor by the name or food item and the location less than the radius selected
            # NB: the user_profile__location is the field in the userprofile model
            # .annotate was added because there is no field inUserProfile called distance. There is a field called location
            # we use annotate to assign the value of location to distance which is an extra field added. This is the distance betwwen the
            # user and the vendor
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True, user_profile__location__distance_lte=(pnt, D(km=1000))).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for v in vendors:
                v.kms = round(v.distance.km, 1)

        # ----------------------------------------------------------------------------------------------------------------
       
       
    

    else:
    # i started with this

        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    # ----------------------------------------------------------------------------
  
    return render(request, 'home.html', {
        'vendors':vendors,
                
    })