from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import UserForm, UserProfileForm
from . forms import VendorForm
from accounts.models import User, UserProfile
from django.contrib import messages
from accounts.utils import send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts import views as AccountsViews
from . models import Vendor
from menu.models import Category, Product
from menu.forms import CategoryForm
from django.template.defaultfilters import slugify

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
        messages.warning(redirect, "You are already logged in")
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
@login_required
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
@login_required
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
            #generate the slug based on the category name
            category.slug = slugify(category_name)
            # save the form
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
            return render(request, 'vendors/add_category.html',{
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

def delete_category(request, pk=None):
    #get the particular category using the primary key. This pk is obtained when the user clicks on the items link
    category = get_object_or_404(Category, pk=pk)
    #delete the category
    category.delete()
    messages.success(request, "Category has been deleted successfully")
    return redirect('menu_builder')
