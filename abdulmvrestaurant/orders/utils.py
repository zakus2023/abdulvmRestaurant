import datetime

import simplejson as json

def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S') # this will be like 20240820114113 year month day hour minutes seconds
    order_number = current_datetime + str(pk)
    return order_number



# this function was created in the final stages. it will be used to get the totals for all the vendors
# I need this for the email template

def order_total_by_vendor(order, vendor_id):

    sub_total = 0
    tax = 0
    tax_dict = {}

    total_data = json.loads(order.total_data)
    # filter the total data using the vendor id and the order. NB the total data might consist of more than one vendors
    # because the order might consist of different vendors products
    data = total_data.get(str(vendor_id))


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
                
            