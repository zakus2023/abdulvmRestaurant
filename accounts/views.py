from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages, auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


# Create your views here.

#this will rstrict the vendor from accessing the customer page

def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

#this will rstrict the customer from accessing the vendor page


def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
     #check if user is already logged in
    if request.user.is_authenticated:
        messages.warning(redirect, "You are already logged in")
        return redirect('dashboard')
    
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            #creating the user using the form directly

            # user = form.save(commit=False)
            # #get the password
            # password = form.cleaned_data['password']
            # #hash the password
            # user.set_password(password)
            # #set the role to customer
            
            # user.role = User.CUSTOMER
            # #save the user
            # user.save()

            # creating the user using the create_user method defined in the models.py
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, phone_number=phone_number, password=password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "User created successfully!")

            return redirect('registerUser')
        else:
            print(form.errors)
        
    else:
        form = UserForm()
    return render(request, 'accounts/registerUser.html',{
            'form' : form
    })


def login(request):
    #check if user is already logged in
    if request.user.is_authenticated:
        messages.warning(redirect, "You are already logged in")
        return redirect('myaccount')
    
    elif request.method == 'POST':
        #get email and password from the form
        email = request.POST['email']
        password = request.POST['password']

        #check if user and password are correct
        user = auth.authenticate(email=email, password=password)
        #the above checks the email and password and returns the user with the matched credentilas

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect('myaccount')

        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')



def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out!")
    return redirect('login')

#this function will redirect user based on the role
#the @login... will send the user to the login page if not logged in
@login_required(login_url='login')
def myaccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custdashboard(request):
    return render(request, 'accounts/custdashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')