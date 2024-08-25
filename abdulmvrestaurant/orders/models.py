from django.db import models

# Create your models here.

from django.db import models
from accounts.models import User
from menu.models import Product

from vendors.models import Vendor
import simplejson as json

# this was added during v dashboard
# this will be used in the request_object.py file
request_object = ''


class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('RazorPay', 'RazorPay'), # Only for Indian Students.
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    # this field was added to hold the vendors. it was added when i was working on the v dashboard later in the project
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    province = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    total = models.FloatField()
    tax_data = models.JSONField(blank=True, null=True, help_text = "Data format: {'tax_type':{'tax_percentage':'tax_amount'}}")
    total_tax = models.FloatField()
    # this field was added to hold the specific vendor tax and revenue. it was added when i was working on the v dashboard later in the project
    total_data = models.JSONField(blank=True, null=True)
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Concatenate first name and last name
    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'
    # this member function i created just befor working on the v dashboard. it is to display all the vendors for a particular order in the
    # admin panel without going into the order. copy this order_placed_to and paste it in the OrderAdmin list display in the admin.py
    def order_placed_to(self):
        return " , ".join([str(i) for i in self.vendors.all()])
    
    # this member funct will be used to show the total for a specific vendor. thiswas added during v dashboard
    def get_total_by_vendor(self):

        sub_total = 0
        tax = 0
        tax_dict = {}


        # to access request inside a django model. you fisrt have to create a custom middleware((request_object) inside the order folder
        # requset_object is initialized at the top
        # get the vendor
        vendor = Vendor.objects.get(user=request_object.user)

        # check if the order has total_data
        if self.total_data:

            # get the total data from this same order model
            total_data = json.loads(self.total_data)

            # filter the total data using the vendor id. NB the total data might consist of more than one vendors
            # because the order might consist of different vendors products
            data = total_data.get(str(vendor.id))

            # # calculate

            
            for key, val in data.items():
                # print(key, val) when printed you will get a data like below.
                # 600 is the subtotal(key) for the vendor,[ PST, HSTGST are tax types, 5.00 and 13.00 are tax percentages, 30 and 78 are tax amounts] which represent the val
                    # key                   val
                # {'600.00': "{'PST': {'5.00': '30'}, 'HSTGST': {'13.00': '78'}}"}

                # add the key which is the subtotal to the subtotal. convert it to float
                sub_total += float(key)
                # add the val which is the tax-dict to the tax_dict by updating it because it is a dict
                val = val.replace("'",'"')
                val = json.loads(val)
                tax_dict.update(val)

                # print(val) val will look like this
                # {'PST': {'5.00': '30'}, 'HSTGST': {'13.00': '78'}}

                # calculate tax

                for i in val:
                    # print(i)  i will look like this. That will give the tax types
                    # PST
                    # HSTGST     
                    for j in val[i]:
                        # print(j)   j will look like below. that will give the tax percentage
                        # 5.00
                        # 13.00

                        # print(val[i][j]) this will get you the tax amounts as below
                        # 30
                        # 78

                        tax += float(val[i][j])
                        # print(tax) the total tax will be 108. the 30 is the first tax + 78 will give 108
                        # 30.0
                        # 108.0
        #  get the grand_total
        grand_total = float(sub_total) + float(tax)

        # print(sub_total)
        # print(tax)
        # print(tax_dict)
        # print(grand_total)

        # add sub_total, tax, tax_dict and grand_total to context dictionary
        context = {
            'sub_total': sub_total,
            'tax': tax,
            'tax_dict': tax_dict,
            'grand_total': grand_total,
        }
        return context

    def __str__(self):
        return self.order_number
    



class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.food_title