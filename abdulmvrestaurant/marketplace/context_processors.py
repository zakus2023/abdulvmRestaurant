from .models import Cart, Tax

from menu.models import Product

def get_cart_counter(request):

    cart_count = 0
    if request.user.is_authenticated:
        try:
            # get the cart items filtererd by the logged in user
            cart_items = Cart.objects.filter(user=request.user)
            # if there is item(s) in the cart
            if cart_items:
                # loop through the cart items
                for cart_item in cart_items:
                    # add the cart quantity to the cart_count
                    cart_count += cart_item.quantity 
            else:
                # if the cart does not have items. set the cart count to 0
                cart_count=0
        except:
            # if there is no item in the cart
            cart_count =0
        
    return dict(cart_count=cart_count)


# get the cart amount or order amount
# this function will be called anytime we click on the add_to_cart, 
# remove_from_cart and delete_from_cart button

# def get_cart_amount(request):
#     subtotal = 0
#     tax = 0
#     grand_total = 0
#     # create and initialize the tax dictionary here

#     if request.user.is_authenticated:
#         cart_items = Cart.objects.filter(user=request.user)
#         for item in cart_items:
#             product = Product.objects.get(pk=item.product.id)
#             subtotal += (product.price * item.quantity)

        
#         # get the tax type and percentage from the db filter by is_active
#         # get_tax = Tax.objects.filter(is_active=True)
#         # # loop through the tax and get the items
#         # for tx in get_tax:
#         #     tax_type = tx.tax_type
#         #     tax_percent = tx.tax_percentage

#         #     # calculate the tax
#         #     tax_amount = ((tax_percent * subtotal)/100, 2)
#         #     tax_dict.update({tax_type: {tax_percent: tax_amount}})
            
#         #     # get total tax
#         #     tax=0
#         #     for key in tax_dict.values():
#         #         for x in key.values():
#         #             tax = tax + x
#         #     print(tax)            

#         # grand_total = subtotal + tax

#         get_tax = Tax.objects.filter(is_active=True)

#         tax_dict = {}
#         tax = 0  # Initialize the total tax

#         # Loop through the tax and get the items
#         for tx in get_tax:
#             tax_type = tx.tax_type
#             tax_percent = tx.tax_percentage

#             # Calculate the tax and round to 2 decimal places
#             tax_amount = round((tax_percent * subtotal) / 100, 2)
#             tax_dict[tax_type] = {str(tax_percent): tax_amount}

#             # Sum up the total tax
#             for key in tax_dict.values():
#                 for x in key.values():
#                     tax += x

#         # Calculate the grand total
#         grand_total = subtotal + tax


#     return  dict(subtotal = subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}  # Initialize the tax dictionary

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            product = Product.objects.get(pk=item.product.id)
            subtotal += (product.price * item.quantity)

        get_tax = Tax.objects.filter(is_active=True)
        tax = 0  # Initialize the total tax

        # Loop through the tax and get the items
        for tx in get_tax:
            tax_type = tx.tax_type
            tax_percent = tx.tax_percentage

            # Calculate the tax and round to 2 decimal places
            tax_amount = round((tax_percent * subtotal) / 100, 2)
            tax_dict[tax_type] = {str(tax_percent): tax_amount}

            # Sum up the total tax
            for key in tax_dict.values():
                for x in key.values():
                    tax += x

        # Calculate the grand total
        grand_total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
