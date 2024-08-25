from django.contrib import admin
from .models import Payment, Order, OrderedFood

# Register your models here.


# # Breakdown of the Code
# OrderedFoodInline Class (admin.TabularInline):

# Purpose: This class is used to define an inline interface for the OrderedFood model in the Django admin.
# model = OrderedFood: Specifies that this inline will be managing instances of the OrderedFood model.
# admin.TabularInline: This is a subclass of admin.InlineModelAdmin that displays the inline related objects in a table format. It’s useful for displaying and editing related objects on the same page as the parent model.
# Example in Admin Interface:

# When you open an Order object in the Django admin, the OrderedFoodInline allows you to manage OrderedFood objects (which are associated with that order) directly on the order's admin page in a tabular format.
# OrderAdmin Class (admin.ModelAdmin):

# Purpose: This class customizes the admin interface for the Order model.
# list_display: This is a list of fields from the Order model that will be displayed in the list view of the Django admin.

class OrderedFoodInline(admin.TabularInline):
    model  = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'product', 'quantity', 'price', 'amount')
    # removes the extra blank fields
    extra = 0

# order_placed_to was added just before working on the v dashboard
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'email', 'total', 'payment_method', 'status', 'order_placed_to', 'is_ordered']
    inlines = [OrderedFoodInline]

admin.site.register(Payment)
admin.site.register(Order,  OrderAdmin)
admin.site.register(OrderedFood)