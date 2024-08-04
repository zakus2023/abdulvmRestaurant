from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.contrib import messages

# Create your views here.

def registerUser(request):
    if request.method == 'POST':
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
