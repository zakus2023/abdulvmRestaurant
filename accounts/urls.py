from django.urls import path
from . import views


urlpatterns = [
    path('registerUser/', views.registerUser, name='registerUser'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myaccount', views.myaccount, name='myaccount'),
    path('custdashboard/', views.custdashboard, name='custdashboard' ),
    path('vendorDashboard/', views.vendorDashboard, name='vendorDashboard' )
]