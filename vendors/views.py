from django.shortcuts import render, redirect
from accounts.forms import UserForm
from . forms import VendorForm
from accounts.models import User, UserProfile
from django.contrib import messages

# Create your views here.

def registerVendor(request):
    if request.method == 'POST':
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

