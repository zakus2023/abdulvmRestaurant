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
    path('registerVendor', views.registerVendor, name='registerVendor'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.products_by_category, name='products_by_category'),


    # category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Food or products CRUD
    path('menu-builder/products/add/', views.add_products, name='add_products'),
    path('menu-builder/products/edit_products/<int:pk>/', views.edit_products, name='edit_products'),
    path('menu-builder/products/delete_products/<int:pk>/', views.delete_product, name='delete_product'),
]