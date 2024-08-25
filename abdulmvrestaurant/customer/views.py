from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from django.contrib import messages
from orders.models import Order
from orders.models import OrderedFood
import simplejson as json

# Create your views here.

@login_required(login_url='login')
def cprofile(request):

    profile= get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_info_form.is_valid():
            profile_form.save()
            user_info_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_info_form.errors)
    else:        
        profile_form = UserProfileForm(instance=profile)
        user_info_form = UserInfoForm(instance=request.user)
        return render(request, 'customer/cprofile.html',{
            'profile_form':profile_form,
            'user_info_form':user_info_form,
            'profile':profile,
        
        })
    

    # my orders

def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_count = orders.count()
    return render(request, 'customer/my_orders.html',{
        'orders':orders,
        'orders_count':orders_count,
    })

    # order details view

def order_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        sub_total = 0
        for item in ordered_food:
            sub_total += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)


        print(ordered_food)
        return render(request, 'orders/order_details.html',{
            'order': order,
            'ordered_food':ordered_food,
            'sub_total':sub_total,
            'tax_data':tax_data,
        })
    except:
        return redirect('custdashboard')
    