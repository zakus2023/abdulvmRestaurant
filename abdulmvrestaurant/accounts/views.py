from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages, auth
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendors.models import Vendor
from orders.models import Order
import datetime

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

            #Send verification email
            mail_subject = 'Activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "User created successfully!")

            return redirect('registerUser')
        else:
            print(form.errors)
        
    else:
        form = UserForm()
    return render(request, 'accounts/registerUser.html',{
            'form' : form
    })


#This funtion activate the user
def activate(request, uidb64, token):
    #This is going to activate the user by setting the is_active to true
    try:
        #decode the uid
        uid = urlsafe_base64_decode(uidb64).decode()
        #get the current user pk and copare it to the decoded pk(uid)
        user = User._default_manager.get(pk=uid)
    except(TabError, ValueError,OverflowError, User.DoesNotExist):
        user = None
    #compare the decode token with the user
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations your account has been activated")
        return redirect('myaccount')
    else:
        messages.error(request, "Invalid or expired activation link")






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
    # get all orders for the user
    orders = Order.objects.filter(user= request.user, is_ordered=True).order_by('-created_at')
    # show only 5 orders for recent orders
    recent_orders = orders[:5]
    # get the number of orders
    orders_count = orders.count()
    return render(request, 'accounts/custdashboard.html',{
        'orders':orders,
        'recent_orders':recent_orders,
        'orders_count':orders_count,
    })

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    # get the logged in vendor
    vendor = Vendor.objects.get(user=request.user)
    
    # get all orders that belongs to the logged in vendor
    #     Query Breakdown:
    # Order.objects.filter(...): This part starts with the Order model and uses the filter() method to retrieve a queryset of Order objects that meet the specified conditions.

    # vendors__in=[vendor.id]:

    # vendors is assumed to be a ManyToManyField in the Order model, relating orders to multiple vendors.
    # vendors__in=[vendor.id] filters the orders to include only those that have the specified vendor.id in their list of associated vendors.
    # vendor.id is the ID of a particular Vendor object, so this condition filters orders that are associated with that vendor.
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders =orders[:5]

    # get current month's revenue

    # first get the current month
    current_month = datetime.datetime.now().month

    # get current months orders for the logged in vendor

    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    
    current_month_revenue = 0

    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']


    # get the total revenue for vendor
    
    total_revenue = 0
    # loop through the orders
    for i in orders:
        # get_total_by_vendor is from the member function in the order model
        total_revenue += i.get_total_by_vendor()['grand_total']
    
    return render(request, 'accounts/vendorDashboard.html',{
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue':current_month_revenue,
    })

#Reset password-----------------------------------------------------

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            #send reset password email
            mail_subject = 'Reset your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Password reset link has been sent to your email")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist")
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html')

#rest password
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            #this will get the primary key of the user whose password is being reset.
            #this uid was obtained and stored in the session in the reset password validate view below
            #thats after decoding the uidb64 which was decoded during creation of the link
            pk = request.session.get('uid')
            #find the user whose primary key is pk
            user = User.objects.get(pk=pk)
            #set the password update
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful!")
            return redirect('login')
        else:
            messages.error(request, 'The two passwords do not match')
            return redirect('reset_password')


    return render(request, 'accounts/reset_password.html')



#when the user clicks on the password reset link the request comes here
#this function validates the request by decoding the token
def reset_password_validate(request, uidb64, token):
    try:
        #decode the uid
        uid = urlsafe_base64_decode(uidb64).decode()
        #get the current user pk and copare it to the decoded pk(uid)
        user = User._default_manager.get(pk=uid)
    except(TabError, ValueError,OverflowError, User.DoesNotExist):
        user = None
    #compare the decode token with the user
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, "Reset password link expired or is invalid")
        return redirect('myaccount')