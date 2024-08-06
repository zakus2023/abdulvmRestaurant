from django.shortcuts import render, redirect
from accounts.forms import UserForm
from . forms import VendorForm
from accounts.models import User, UserProfile
from django.contrib import messages
from accounts.utils import send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts import views as AccountsViews

# Create your views here.

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
    return render(request, 'vendors/vprofile.html')