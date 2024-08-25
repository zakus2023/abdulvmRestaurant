from django.shortcuts import render, get_object_or_404, redirect
from vendors.models import Vendor
from menu.models import Category, Product
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amount
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from datetime import date, datetime
from accounts.models import UserProfile

# imports to create the point
from django.contrib.gis.geos import GEOSGeometry
# D is the shortcut for distance
from django.contrib.gis.measure import D 
from django.contrib.gis.db.models.functions import Distance
from vendors.models import OpeningHours
from orders.forms import OrderForm

# Create your views here.

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    return render(request, 'marketplace/listings.html',{
        'vendors':vendors,
        'vendor_count':vendor_count,
    })


#  I commented this after i created the is_open member function in the vendor model
# vendor details view''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def vendor_detail(request, vendor_slug):
    
  
    #the vendor slug is coming from the request. 
    # so get the vendor whose vendor slug is equal to the one from the request
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    # the prefetch related will look for the data in a reverse manner.Reverse lookup
    # here we are fetching the categories that belongs to the vendor. I added the related_name=product to the 
    # Product model. This is because we dont have access to the food item in the category. but since i want to have the 
    # food items that belongs to a particular category I have to access the food item from the category model based on the related name.
    # in the prefetch if i use only 'product' it will fetch all products that belong to that categroy for that particular user, 
    # but i want to get only products that are avilable
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'product', 
            queryset= Product.objects.filter(is_available=True)
        )
    )

    # get the opning hours for this vendor
    opening_hours = OpeningHours.objects.filter(vendor=vendor).order_by('day', '-from_hour')
    # check current day's opening hours
    # get current day's date as today. We dont want the days name but the day's number
    todays_date = date.today()
    # get the day of the weeks number
    today = todays_date.isoweekday()
    # filter the opening hours with the vendor and day of the week and pass it as contect dictionary 
    current_days_opening_hours = OpeningHours.objects.filter(vendor=vendor, day=today)


    # --------------------------------------------------------------------------------------------------

    # show whether the vendor is opened or not on the home page
    # get the current time
    # now = datetime.now()
    # # convert the the current time to string and set the format to 24h
    # current_time = now.strftime("%H:%M:%S")
    
    # # set is opened to None. This is a viariable we are declaring for the first time 
    
    # # through the currenet_opening_hours and check if the current time falls within it
    # is_open = None
    # for i in current_days_opening_hours:
    #     # set the opening time to compare with. That should be the from_hour. Then convert it to the required format
    #     # the conversion should be as it was converted to be stored in the db. ,time() will get you only the time
    #     # str(datetime...) this will convert it to str. strptime will string format it.
    #     opening_time = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
    #     # get the closing time compare with. That should be the from_hour. Then convert it to the required format
    #     closing_time = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

    #     # check if the current time is within the opening and closing time
    #     if current_time > opening_time and current_time < closing_time:
    #         is_open = True
    #         break
    #     else:
    #         is_open = False
    # ------------------------------------------------------------------------------------------


    # get the cart items to be used inside this vendor_details template
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items=None
    return render(request, 'marketplace/vendor_details.html',{
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
        'opening_hours':opening_hours,
        'current_days_opening_hours':current_days_opening_hours,
        
    })


def add_to_cart(request, product_id):
    # check if user is authenticated
    if request.user.is_authenticated:
        # return JsonResponse({'status':'Success', 'message':'User is logged in'})
            # then check if request is from ajax request
        # if request.is_ajax(): deprecated. for django 3.1+ use the one below
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # get the product using the product_id obtianed from the ajax request as filter
                product = Product.objects.get(id=product_id)
                
                # check if the food item is already in the cart
                try:
                    # check if the current user has an item in the cart and also if the particular product with the product_id 
                    # is in the cart
                    chkCart = Cart.objects.get(user=request.user, product=product)
                    
                    # increase cart quantity
                    chkCart.quantity +=1
                                     
                    chkCart.save()
                    # NB: cart_counter: get_cart_counter, qty and get_cart_amount are functions in the marketplace/context_processors.
                    # to use them in any of the functions we must pass them here. in the add_to_cart view, remove from , and delete cart views
                    # after adding it go to the custom.js and use it. thats get it from the response.since here you are passing it as jsonresponse
                    return JsonResponse({'status':'success', 'message':'Item quantity increased successfully', 'cart_counter':get_cart_counter(request), 'qty':chkCart.quantity, 'get_cart_amount':get_cart_amount(request)})
                # if the item is not in the cart or user has not added 
                # that item in the cart run the except part
                except:
                    # create the cart
                    chkCart = Cart.objects.create(user=request.user, product=product, quantity=1)
                    return JsonResponse({'status':'success', 'message':'Product added successfully', 'cart_counter':get_cart_counter(request), 'qty':chkCart.quantity, 'get_cart_amount':get_cart_amount(request)})

            # if the user is not logged in
            except:
                 return JsonResponse({'status':'Failed', 'message':'This food does not exixt'})
        # if request is not from ajax
        else:
             return JsonResponse({'status':'Failed', 'message':'Invalid request'})
    
        
    # NB: Here we are receiving the product_id from the ajax function inside the custom.js
    #we return httpresponse because we dont want to reload the page when the function is called
    else:
        return JsonResponse({'status':'login_required', 'message':'Please login to continue'})
    
    


def remove_from_cart(request, product_id):
    # check if user is authenticated
    if request.user.is_authenticated:
        # return JsonResponse({'status':'Success', 'message':'User is logged in'})
            # then check if request is from ajax request
        # if request.is_ajax(): deprecated. for django 3.1+ use the one below
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # get the product using the product_id obtianed from the ajax request as filter
                product = Product.objects.get(id=product_id)
                
                # check if the food item is already in the cart
                try:
                    # check if the current user has an item in the cart and also if the particular product with the product_id 
                    # is in the cart
                    chkCart = Cart.objects.get(user=request.user, product=product)
                    
                    # decrease cart quantity for that particular item
                    # chech if the quantity of items in the cart is greater than 1 for that particular item
                    if chkCart.quantity > 1:
                        # decrease it by 1 for that particular item
                        chkCart.quantity -=1
                        # save it for that particular item
                        chkCart.save()
                    else:
                        # delete the cart if the quantity is less than 1 for that particular item
                        chkCart.delete()
                        # set the quantity of items in the cart to 0 for that particular item
                        chkCart.quantity = 0                                                     
                   
                    # NB in order to increase the value of the quantity in the cart without reloading the page I added
                    # 'cart_counter:cart_counter' and imported it from the context_procesoors. I also updated the custom
                    # java script(ajax requset function) to place the cart_count in the badge when the value changes. the same this i did for the remove
                    return JsonResponse({'status':'success', 'message':'Item quantity decreased successfully', 'cart_counter':get_cart_counter(request), 'qty':chkCart.quantity, 'get_cart_amount':get_cart_amount(request), 'get_cart_amount':get_cart_amount(request)})
                # if the item is not in the cart or user has not added 
                # that item in the cart run the except part
                except:
                    
                    # chkCart = Cart.objects.create(user=request.user, product=product, quantity=1)
                    return JsonResponse({'status':'Failure', 'message':'This item is not in the cart'})

            # if the user is not logged in
            except:
                 return JsonResponse({'status':'Failed', 'message':'This food does not exixt'})
        # if request is not from ajax
        else:
             return JsonResponse({'status':'Failed', 'message':'Invalid request'})
    
        
    # NB: Here we are receiving the product_id from the ajax function inside the custom.js
    #we return httpresponse because we dont want to reload the page when the function is called
    else:
        return JsonResponse({'status':'login_required', 'message':'Please login to continue'})
    

# view for cart page
@login_required(login_url='login')
def cart_page(request):
    # get all the items in the cart that belongs to the logged in user
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'marketplace/cart_page.html',{
        'cart_items':cart_items,
    })
    

# this will delete the entire cart item. That is for a particular item when the quantity is zero

def delete_cart_item(request, product_id):
   
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # check if the item is in the cart using the product_id from the request to filter
                cart_item = Cart.objects.get(user=request.user, id=product_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'success', 'message':'Item deleted successfully', 'cart_counter':get_cart_counter(request), 'get_cart_amount':get_cart_amount(request)})
            except:
                return JsonResponse({'status':'failure', 'message':'This item is not in the cart'})

        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})
    

    # search function

def search(request):
    # redirect the user to the market place page if he only enters 127.0.0.1:8000/search
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        # else do run the codes below

        # get the name search query from the request when the search button on the homepage is clicked
        # the address is the name of the address input. Also use the names of the other inputs to get their values from the search quesry
        # request.GET meaning from the url get the search query
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        key_word = request.GET['restaurant_name']

        # search vendor based on food item
        # get vendor ids that has the food item the user has typed in the keyword
        # first get the food item that matches what the user types in the keyword
        # .values_list('vendor', flat=True) : the product has a field called vendor. This means get the list of
        # vendors with the searched food item

        vendor_by_food_item = Product.objects.filter(food_title__icontains=key_word, is_available=True).values_list('vendor', flat=True)
        
        # search the vendor based on the keyword/ the key word is using the id obtained from the above function 
        # and gettin the vendor based on the function below. the two filters are combined usin the Q() and | or.
        # get the restaurants whose name contain the keyword, and whose vendor is approved and is active user
        # NB: user__is_active: the vendor model has a field called user which is a 
        # one_to_one field of the User model And the user Model has a field called is_active
        # id__in = means if the id of the vendor is equal to the id obtained from the function above

        vendors = Vendor.objects.filter(Q(id__in=vendor_by_food_item) | Q(vendor_name__icontains=key_word, is_approved=True, user__is_active=True))
        
        # creating the point and searching the restaurant by the location
        # check if there is latitude, longitude and radius then filter the vendors by the point/location, name, food
        if latitude and longitude and radius:
            # using %s because we want to use string replacement technique so that we can pass the dynamic values.
            # pnt = GEOSGeometry('POINT(-96.876369 29.905320)', srid=4326)
            # the longitude must be passed first
            pnt = GEOSGeometry('POINT(%s  %s)' %(longitude, latitude))
            
            # filter the vendor by the name or food item and the location less than the radius selected
            # NB: the user_profile__location is the field in the userprofile model
            # .annotate was added because there is no field inUserProfile called distance. There is a field called location
            # we use annotate to assign the value of location to distance which is an extra field added. This is the distance betwwen the
            # user and the vendor
            vendors = Vendor.objects.filter(Q(id__in=vendor_by_food_item) | Q(vendor_name__icontains=key_word, is_approved=True, user__is_active=True), 
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

    # get the distance between the restaurant and the source location

    # This line of code is iterating over a queryset of vendors and assigning a new attribute kms to each vendor object. Here's a breakdown of what it does:

    # 1. for v in vendors:
    # This starts a loop that goes through each vendor object in the vendors queryset.
    # v represents the current vendor object in each iteration.
    # 2. v.kms = v.distance.km
    # v.distance:
    # This refers to the distance attribute that was added to each vendor object earlier using the .annotate(distance=Distance("user_profile__location", pnt)) part of the query.
    # distance is an object that represents the distance between the vendor's location and the specified point pnt.
    # v.distance.km:
    # This accesses the distance in kilometers. The km attribute is provided by the Distance object in Django's GeoDjango module, which allows you to get the distance in various units, such as kilometers, meters, miles, etc.
    # v.kms = v.distance.km:
    # This assigns the distance in kilometers to a new attribute kms on the vendor object. After this assignment, each v object will have a kms attribute that represents how far away the vendor is from the specified point pnt in kilometers.
    # Purpose of This Code
    # The main purpose of this code is to make it easier to access the distance in kilometers for each vendor object. By creating a kms attribute, you can directly use v.kms in templates, views, or further processing without needing to access the more complex v.distance.km each time.


            for v in vendors:
                v.kms = round(v.distance.km, 1)
        # make sure to use the vendor.kms in the listings.html to show the distance

        # vendors = Vendor.objects.filter(vendor_name__icontains=key_word, is_approved=True, user__is_active=True)

        vendor_count = vendors.count()

        return render(request, 'marketplace/listings.html',{
            'vendors':vendors,
            'vendor_count':vendor_count,
            'source_location': address,
        })
        


# checkout view
@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    # the main info of the logged in user is in the context processor. usin user.... you can get 
    # the basic user infor in all the html files. Use userprofile the get the other details
    # get all infor from Userprofile where user is the logged in user

    #NB here we are assigning the values of User Model, UserProfile model to Order model


    user_profile= UserProfile.objects.get(user= request.user)
    # when the order form is empty or loaded assign the following values.initial values
    default_values = {
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.address,
        'country':user_profile.country,
        'province':user_profile.province,
        'city':user_profile.city,
        'postal_code':user_profile.postal_code,
    }
    form = OrderForm(initial= default_values)
    return render(request, 'marketplace/checkout.html',{
        'form':form,
        'cart_items':cart_items
    })