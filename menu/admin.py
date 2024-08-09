from django.contrib import admin
from .models import Category, Product

# Register your models here.

#add this class to generate the slug automatically. make sure to pass this slug in the admin.site.register of Category
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}

    # show the following fields in the db display

    list_display = ('category_name', 'vendor', 'updated_at')

    #add search field
    search_fields = ('category_name', 'vendor__vendor_name')

    # ---------------------------------------------------------------------------------------------------------

#add this class to generate the slug automatically. make sure to pass this slug in the admin.site.register of product
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_title',)}

    # show the following fields in the db display

    list_display = ('food_title', 'vendor', 'price', 'category', 'is_available',  'updated_at')

    #add search field
    search_fields = ('food_title', 'category__category_name','vendor__vendor_name', 'price')
    list_filter = ('is_available',)


#register the models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
