from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import UserForm, UserProfileForm
from . forms import VendorForm, OpeningHoursForm
from accounts.models import User, UserProfile
from django.contrib import messages
from accounts.utils import send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts import views as AccountsViews
from . models import Vendor, OpeningHours
from menu.models import Category, Product
from menu.forms import CategoryForm, ProductForm
from django.template.defaultfilters import slugify
# for testing
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError

from orders.models import Order, OrderedFood



# Create your views here.


# this was added later to get the id of the logged in user in this case the vendor. 
# This function will be called anytime we need to get the id of the current vendor

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


#===================================================================================

def registerVendor(request):
    #check if user is already logged in
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('myaccount')
    
    elif request.method == 'POST':
    #store the data and create the user
        #this one is to store the data from the user form part
        form = UserForm(request.POST)
        #this one is to store the data from the user form part. request.FILES is added because we want to save the file which is the license
        vendor_form = VendorForm(request.POST, request.FILES)
        #check both forms to see if there are no errors
        if form.is_valid() and vendor_form.is_valid():
            #first save the user info
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, phone_number=phone_number, password=password)
            user.role = User.VENDOR
            user.save()
            #then save the vendor info
            vendor = vendor_form.save(commit=False)
            #get the user for the particular vendor
            vendor.user = user
            #get the vendor name from the data entered by the user
            vendor_name = vendor_form.cleaned_data['vendor_name']
            #convert the vendor name into slug. convert the user id to string and add it to the slug to make it unique
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            #get the userprofile for the created user and asssign it to the vendor
            user_profile = UserProfile.objects.get(user=user)
            #assign it
            vendor.user_profile = user_profile
            vendor.save()

            #Send verification email
            mail_subject = 'Activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)


            messages.success(request, 'Your account has been successfully created!')
            return redirect('registerVendor')

        else:
            print(form.errors)


    else:
        #get the data
        form = UserForm()
        vendor_form = VendorForm()

    return render(request, 'vendors/registerVendor.html',{
        'form': form,
        'vendor_form':vendor_form
    })




#vendor profile view

#to get the check_role_vendor I imported all the views in the accounts app into this views as AccounttsViews.
check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):

    # to update the vendor and userprofile we must get the vendor and userprofile of the logged in user
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    #updating the userprofile and vendor info
    #check if the user has clicked update btn
    if request.method == 'POST':
        #get the data in the form, the files and the original data that was already present in the db which was not changed and keep it profile_form
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings updated")
            return redirect('vprofile')

        else:
            print(profile_form.errors)
            print(vendor_form.errors)

            return render(request, 'vendors/vprofile.html', {
                'profile_form': profile_form,
                'vendor_form': vendor_form,
                'profile': profile,
                'vendor': vendor,
            })

    else:   

        #show the current values inside the fields by passing them as instances to the forms before passing the forms as context dics to the template
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
        return render(request, 'vendors/vprofile.html',{
            'profile_form':profile_form,
            'vendor_form':vendor_form,
            'profile':profile,
            'vendor':vendor,
        })
    

# menu builder view

check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    # get the logged in user
    vendor = get_vendor(request)
    # get all the categories of the vendor who is logged in
    categories = Category.objects.filter(vendor=vendor).order_by('updated_at')

    return render(request, 'vendors/menu-builder.html',{
        'categories':categories
    })


# get products by category

check_role_vendor = AccountsViews.check_role_vendor
@login_required
@user_passes_test(check_role_vendor)
def products_by_category(request, pk=None):
    # get the id of the vendor who is logged in. I am using the get_vendor function created at the top
    vendor = get_vendor(request)
    # get the primary key of the selected category
    category = get_object_or_404(Category, pk=pk)
    # get all the products under the category and of the logged in user
    products = Product.objects.filter(vendor=vendor, category=category)
    return render(request, 'vendors/products_by_category.html',{
        'products':products,
        'category':category,
    })


# Category CRUD
check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    # check if the user has clicked on creat button
    if request.method == 'POST':
        # pass all the data in the form to the category form and store it in the form variable
        form = CategoryForm(request.POST)
        # check if the form is filled well or has data in it
        if form.is_valid():
            # save the data in the category variable but don't commit into database until other required info is added
            category = form.save(commit=False)
            # get the logged in vendor and add the id to the data inside the category variable
            category.vendor = get_vendor(request) 
            #generate the slug and add it to the data to be saved
            # first get the category name entered by the user
            category_name = form.cleaned_data['category_name']

            # when you save the category an id will be generated
            category.save()
            #generate the slug based on the category name and add the id of the category to it to make it unique
            category.slug = slugify(category_name)+ '-'+str(category.id)
            # save the category again
            category.save()
            
            # dispaly a success message to the user
            messages.success(request, "Category created succesfully")
            # redirect the user to the menu bulder page
            return redirect('menu_builder')
        else:
            # rerender the form with the errors         
            return render(request, 'vendors/add_category.html',{
            'form':form
        })            
        
    # otherwise show the user the form to be filled
    else:
        form = CategoryForm()
        return render(request, 'vendors/add_category.html',{
            'form':form
        })
    
#edit category
check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    #get the category instance based on the primary key
    category = get_object_or_404(Category, pk=pk)
    # check if the user has clicked on creat button
    if request.method == 'POST':
        # pass all the data in the form to the category form and store it in the form variable. 
        # instnace=instance adds the already existing data that did not change
        form = CategoryForm(request.POST, instance=category)
        # check if the form is filled well or has data in it
        if form.is_valid():
            # save the data in the category variable but don't commit into database until other required info is added
            category = form.save(commit=False)
            # get the logged in vendor and add the id to the data inside the category variable
            category.vendor = get_vendor(request) 
            #generate the slug and add it to the data to be saved
            # first get the category name entered by the user
            category_name = form.cleaned_data['category_name']
            #generate the slug based on the category name
            category.slug = slugify(category_name)
            # save the form
            category.save()
            # dispaly a success message to the user
            messages.success(request, "Category updated succesfully")
            # redirect the user to the menu bulder page
            return redirect('menu_builder')
        else:
            # rerender the form with the errors         
            return render(request, 'vendors/edit_category.html',{
            'form':form
        })            
        
    # otherwise show the user the form to be filled
    else:
        form = CategoryForm(instance=category)
        return render(request, 'vendors/edit_category.html',{
            'form':form,
            'cat':category,
        })
    
    #delete category
check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    #get the particular category using the primary key. This pk is obtained when the user clicks on the items link
    category = get_object_or_404(Category, pk=pk)
    #delete the category
    category.delete()
    messages.success(request, "Category has been deleted successfully")
    return redirect('menu_builder')

# Products CRUD
# ============================================================
#add product
check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_products(request):
    if request.method == 'POST':
        # pass all the data in the form to the category form and store it in the form variable
        form = ProductForm(request.POST, request.FILES)
        # check if the form is filled well or has data in it
        if form.is_valid():
            # save the data in the category variable but don't commit into database until other required info is added
            product = form.save(commit=False)
            # get the logged in vendor and add the id to the data inside the category variable
            product.vendor = get_vendor(request) 
            #generate the slug and add it to the data to be saved
            # first get the category name entered by the user
            food_title = form.cleaned_data['food_title']
            #generate the slug based on the category name
            product.slug = slugify(food_title)
            # save the form
            product.save()
            # dispaly a success message to the user
            messages.success(request, "Product created succesfully")
            # redirect the user to the menu bulder page
            return redirect('products_by_category', product.category.id)
        else:
            # rerender the form with the errors         
            return render(request, 'vendors/add_product.html',{
            'form':form
        })            
        
    # otherwise show the user the form to be filled
    else:
        form = ProductForm()
        #modify the form to show only categories that velongs to the current user
        form.fields['category'].queryset = Category.objects.filter(vendor= get_vendor(request))
        return render(request, 'vendors/add_product.html',{
            'form':form
        })
    

#edit_product
check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_products(request, pk=None):
    #get the category instance based on the primary key
    product = get_object_or_404(Product, pk=pk)
    # check if the user has clicked on creat button
    if request.method == 'POST':
        # pass all the data in the form to the category form and store it in the form variable. 
        # instnace=instance adds the already existing data that did not change
        form = ProductForm(request.POST, request.FILES, instance=product)
        # check if the form is filled well or has data in it
        if form.is_valid():
            # save the data in the category variable but don't commit into database until other required info is added
            food = form.save(commit=False)
            # get the logged in vendor and add the id to the data inside the food variable
            food.vendor = get_vendor(request) 
            #generate the slug and add it to the data to be saved
            # first get the category name entered by the user
            food_title = form.cleaned_data['food_title']
            #generate the slug based on the food title
            food.slug = slugify(food_title)
            # save the form
            food.save()
            # dispaly a success message to the user
            messages.success(request, "Product updated succesfully")
            # redirect the user to the menu product by category page
            return redirect('products_by_category', product.category.id)
        else:
            print(form.errors)
            # rerender the form with the errors  
            form.fields['category'].queryset = Category.objects.filter(vendor= get_vendor(request))       
            return render(request, 'vendors/edit_product.html',{
            'form':form,
            'pro':product,
        })            
        
    # otherwise show the user the form to be filled
    else:
        
        form = ProductForm(instance=product)
        form.fields['category'].queryset = Category.objects.filter(vendor= get_vendor(request))
        return render(request, 'vendors/edit_product.html',{
            'form':form,
            'pro':product,
        })
    


#delete product
check_role_vendor = AccountsViews.check_role_vendor
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_product(request, pk=None):
    #get the particular category using the primary key. This pk is obtained when the user clicks on the items link
    product = get_object_or_404(Product, pk=pk)
    #delete the product
    product.delete()
    messages.success(request, "Product has been deleted successfully")
    return redirect('products_by_category', product.category.id)

# ------------------------------------------------------------------------------------------------------
# view for oepning hours

def opening_hours(request):
    form = OpeningHoursForm()
    opening_hours = OpeningHours.objects.filter(vendor=get_vendor(request))
    return render(request, 'vendors/opening_hours.html',{
        'form':form,
        'opening_hours':opening_hours,
    })

# ------------------------------------------------------------------------------------------------------

# add opening hours
# I will use ajax request to call this function in order not to reload the page 
# when this function is called. The ajax request function will be in the 
# custom.js file

def add_opening_hours(request):
    # handle the data received from the ajax request and save them inside the data base

    # check if user is authenticated
    if request.user.is_authenticated:
        # check if request is an ajax request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            # receive the data from the ajax request
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            # i added == 'true to convert the value to boolean
            is_closed = request.POST.get('is_closed') == 'true'
            
            try:
                # create and save the hour
                hour = OpeningHours.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                # if it is created successfully
                if hour:
                    # get the id of the day so that you use it to get the name of the day
                    day = OpeningHours.objects.get(id=hour.id)
                    # check if the user selected a day and checked is closed
                    if day.is_closed:
                        # send the day, the iad and closed as is_closed
                        response= {'status':'success', 'id':hour.id, 'day':day.get_day_display(), 'is_closed':'closed'}
                    else:
                        # send the response below
                        response = {'status':'success', 'id':hour.id, 'day':day.get_day_display(), 'from_hour':hour.from_hour, 'to_hour':hour.to_hour}
                
                return JsonResponse(response)
            except IntegrityError as e:
                # response = {'status': 'failed', 'message': from_hour+'-'+to_hour+ ' already exist for '+day.get_day_display()}
                response = {'status':'failed', 'message':f"{from_hour} - {to_hour} already exist for the selected day"}
                return JsonResponse(response)



        else:
            return HttpResponse('Invalid Request')


    return HttpResponse("ADD OH")

# remove opening hours view
# this will be called by the ajax request

def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        # check if request is an ajax request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
            hour = get_object_or_404(OpeningHours, pk=pk)
            # delete the hour from the database. The tr will be removed inside the ajax request function
            hour.delete()
            return JsonResponse({'status':'success', 'id':pk})
        else:
            return JsonResponse({'status':'failed', 'message':'Invalid request'})
    else:
        return JsonResponse({'status':'failed', 'message':'You must be logged in to delete this item'})
    


# order details view

# def vendor_order_details(request, order_number):
#     try:
#         orders = get_object_or_404(Order, order_number=order_number, is_ordered=True)
#         print(orders)
#         ordered_food = OrderedFood.objects.filter(order=orders, product__vendor=get_vendor(request.user))
#         print(ordered_food)
#         return render(request, 'vendors/order_details.html')
#     except:
#         return redirect('vendor')
        
  

def vendor_order_details(request, order_number):
    try:
        # Retrieve the order by order number and ensure it's ordered
        order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
        print(order)
        
        # Retrieve the vendor associated with the current user
        vendor = Vendor.objects.get(user=request.user)
                
        
        # Retrieve ordered food items associated with the order and the current vendor
        ordered_food = OrderedFood.objects.filter(order=order, product__vendor=vendor)
        print(ordered_food)
        
        # Render the template with the order and ordered food items
        return render(request, 'vendors/order_details.html', {
            'ordered_food': ordered_food, 
            'order': order,
            # these are coming from the member function inside the order model
            'sub_total': order.get_total_by_vendor()["sub_total"],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'grand_total': order.get_total_by_vendor()['grand_total']
            })
    
    except Vendor.DoesNotExist:
        # Redirect if vendor does not exist for the current user
        return redirect('vendor')
    except Exception as e:
        # General exception handling with error logging
        print(f"Error: {e}")
        return redirect('vendor')


# my orders(vendor)

def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')

    print(orders)
    return render(request, 'vendors/my_orders.html',{
        'orders':orders,
    })