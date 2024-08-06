from django.urls import path
from . import views
#to have access to all the views inside the accounts app
from accounts import views as AccountsViews

urlpatterns = [
    #this is to forward the user to vendorDashbord when he enters accounts/vendor
    #........................................................
    path('', AccountsViews.vendorDashboard, name='vendor'),
    # ........................................................
    path('profile/', views.vprofile, name='vprofile'),
    path('registerVendor', views.registerVendor, name='registerVendor')
]