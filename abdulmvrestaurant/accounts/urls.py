from django.urls import path, include
from . import views


urlpatterns = [
    #i added the path('', views.myaccount, name='myaccount') this will take when the user enters /account in the url. this will redirect to myaccount
    path('', views.myaccount, name='myaccount' ),
    path('registerUser/', views.registerUser, name='registerUser'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myaccount', views.myaccount, name='myaccount'),
    path('custdashboard/', views.custdashboard, name='custdashboard' ),
    path('vendorDashboard/', views.vendorDashboard, name='vendorDashboard' ),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password', views.reset_password, name='reset_password'),
]