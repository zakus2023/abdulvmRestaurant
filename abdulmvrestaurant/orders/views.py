from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
# to use simple json first pip install simple json
import simplejson as json
from .utils import generate_order_number, order_total_by_vendor
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from menu.models import Product
from marketplace.models import Tax

from accounts.utils import send_notification

# i imported this at the later stages of the project when i was working on the email templates
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.

@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    # get the following from the marketplace/context_processors/get_cart_amount function
    # subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']

    # get the vendors ids in a list
    # initialize the list
    vendors_id = []
    # loop through the cart items 
    for i in  cart_items:
        if i.product.vendor.id not in vendors_id:
        # if a vendor has item in the cart add the vendors id to the list
            vendors_id.append(i.product.vendor.id)
    
# -----------------------------------------------------------------------------
    #  calculating the vendor tax, and total revenues

    # initialize the subtotal to 0
    sub_total=0

    # get the tax which is active. tax tpre : PST and HSTGST, tax percent will be obtained
    get_tax = Tax.objects.filter(is_active=True)

    # initialize the tax_dict to empty dict
    tax_dict = {}

    # initialize total_data
    total_data = {}


    # initialize k . this will hold the dict of the subtotal. it holds the vendor id and the subtotal for the item
    k = {}

    # loop through the cart items

    for i in cart_items:
        # get the product using using the pk. if the pk is in the list of vendors_id obtained above
        # the vendor_id is a field in the products model
        # the vendors_id is the list of vendor ids obtained above
        product = Product.objects.get(pk=i.product.id, vendor_id__in=vendors_id)
        # get the vendor id
        ven_id = product.vendor.id

        # check if the vendor id is in k
        if ven_id in k:
            # assign the ven_id to subtotal as the key
            sub_total = k[ven_id]
            
            # add the results of (product.price * i.quantity) to subtotal as the value
            sub_total += (product.price * i.quantity)

            # assign the value of subtotal to k
            k[ven_id] = sub_total
        else:
             # add the results of (product.price * i.quantity) to subtotal as the value
            sub_total = (product.price * i.quantity)

            # assign the value of subtotal to k
            k[ven_id] = sub_total

        # calculate the tax data

        # first get the tax_data. We will use the 

        for i in get_tax:

            tax_type = i.tax_type
            tax_perecentage = i.tax_percentage
            tax_amount = round((tax_perecentage * sub_total)/100)

            # add tax_type ... to the tax_dict dictionary. we use update for that
            tax_dict.update({ tax_type: {str(tax_perecentage): str(tax_amount)}})

            # form the total_data from the above infor
            # add vendor id , subtotal and tax_dict, ... to the total_data dictionary for each vendor. we use update for that
            total_data.update({product.vendor.id: {str(sub_total): str(tax_dict)}})

        # --------------------------------------------------------------------------------------------------------


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # initialize the order form with the data 

            # this data is from the from the place_order form
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.province = form.cleaned_data['province']
            order.city = form.cleaned_data['city']
            order.postal_code = form.cleaned_data['postal_code']

            # from logged in user
            order.user = request.user

            # from the results of the the marketplace/context_processors/get_cart_amount function
            order.total = grand_total
            # convert this to json format. NB when we are retrieving the tax_data from the db we use json.loads to revert it
            order.tax_data = json.dumps(tax_data)

            # i added during v dashboard
            # add the total data calculated above to the db order model. I use json.dumps because i am storing it as json format
            order.total_data = json.dumps(total_data)

            order.total_tax = total_tax

            # from the place_order.html 
            order.payment_method = request.POST['payment_method']

            # we genrate the order number by calling the function and apssing the order id as the primary key
            
            order.save() # at this stage the order is created after saving 
            # assing the order number genrated after saving to the order number field and save again
            order.order_number = generate_order_number(order.id)

            # add the vendors_id. since it is a many-to-many field this is how we add it to the nodel
            order.vendors.add(*vendors_id)


            order.save()

            return render(request, 'orders/place_order.html',{
                'order': order,
                'cart_items': cart_items,
            })
        else:
            print(form.errors)

    return render(request, 'orders/place_order.html',)



# payments view
@login_required(login_url='login')
def payments(request):
    # check if request is ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
    # store payment details in the payment model. These are from the ajax request which is in the place_order.htnl
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")
        # print(order_number, transaction_id, payment_method, status)

        # get the particular order using the user and the order_number which was created after payment
        order = Order.objects.get(user=request.user, order_number=order_number)

        # create the payment object
        payment = Payment(
            user= request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
     
        # save the payment in the payment model in db
        payment.save()
        

        # update the order model when the payment is successful
        order.payment = payment
        order.is_ordered = True
        order.save()
        
            
        # move the cart items to the ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            # initialize the order table
            ordered_food = OrderedFood()
            # add the values to it
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.product = item.product
            ordered_food.quantity = item.quantity
            ordered_food.price = item.product.price
            ordered_food.amount = item.product.price * item.quantity
            ordered_food.save()
    

    # confirmation email starts here
    # --------------------------------------------------------------------------------------------------------
        # send order confirmation email to the customer/using the send_notification function

    

        mail_subject = 'Order Confirmation'
        mail_template = 'orders/order_confirmation.html'

        # i added this at the final stages when i was sending the email as html formatted
        # --------------------------------------------------------------------------------

        ordered_food = OrderedFood.objects.filter(order=order)
        current_site = get_current_site(request)

        customer_sub_total = 0

        for item in ordered_food:
            customer_sub_total += (item.price * item.quantity)
        
        tax_data = json.loads(order.tax_data)


        # --------------------------------------------------------------------------
        context = {
            'user': request.user,
            'order':order,
            'to_email': order.email,
            'ordered_food':ordered_food,
            'domain': current_site,
            'customer_sub_total':customer_sub_total,
            'tax_data':tax_data,

        }

        send_notification(mail_subject=mail_subject, mail_template=mail_template, context=context)
        

        # send order received email to the vendor
        # here the vendors may be more than one

        mail_subject = 'You have received a new order'
        mail_template = 'orders/new_orders_received.html'

        # initialize the list of vendor emails to empty list
        to_emails = []
        
        # loop through the cart items
        for i in cart_items:
            # check if the email of the vendor is not already in the to_emails list and the vendor is not already in the vendors list
            if i.product.vendor.user.email not in to_emails:
            # for each cart item get the email address of the vendor
                to_emails.append(i.product.vendor.user.email) 

                # vendors ordered food
                ordered_food_to_vendor = OrderedFood.objects.filter(order=order, product__vendor=i.product.vendor)  

        
                context = {
                    'order':order,
                    'to_email': i.product.vendor.user.email,
                    'ordered_food_to_vendor':ordered_food_to_vendor, 
                    'vendor_sub_total': order_total_by_vendor(order, i.product.vendor.id)['sub_total'],
                    'tax_data': order_total_by_vendor(order, i.product.vendor.id)['tax_dict'],
                    'vendor_grand_total': order_total_by_vendor(order, i.product.vendor.id)['grand_total'],
                                       
                }

            send_notification(mail_subject=mail_subject, mail_template=mail_template, context=context)

        
        
        # clear the cart if the pay ment is successful

        cart_items.delete()
       
        # return back to ajax with the status success or failure
        response = {
            'order_number' : order_number,
            'transaction_id' : transaction_id, 
        }
        # this response will be received in the place_order.html ajax request function
        return JsonResponse(response)
    return HttpResponse("Payment")

# order complete
def order_complete(request):
    # these are accessed from the query string. They were passed to the query string during the redirect to
    # the order complete page by the ajax function in the place order page
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    # using the order number and the transaction id search the order
    try:
        # get the order  by suing the trans id and order nmber as well as is ordered should be true
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        # get the ordered food by filtering with the order that was obtained above
        ordered_food = OrderedFood.objects.filter(order=order)

        sub_total = 0
        for item in ordered_food:
            sub_total += (item.price * item.quantity)

        # get the taxData which contains the taxes from the order.
        # i used json.loads to retrieve it because when i was saving i used json.dumbs to save it
        tax_data = json.loads(order.tax_data)

        
        return render(request, 'orders/order_complete.html',{
        'order':order,
        'ordered_food': ordered_food,
        'sub_total': sub_total,
        'tax_data':tax_data,
        })
    except:
        # if there is no order that has the ids above
        return redirect('home')



