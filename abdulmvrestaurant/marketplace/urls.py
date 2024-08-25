from django.urls import path
from . import views

urlpatterns= [
     # cart page url
    path('cart_page/', views.cart_page, name='cart_page'),
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    #add to cart path
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # remove item from cart. This will reduce the cart item count by one
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # delete cart item. This will delete the entire cart item. for particular item
    path('delete_cart_item/<int:product_id>/', views.delete_cart_item, name='delete_cart_item'),
   
]