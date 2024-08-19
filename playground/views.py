from django.shortcuts import render
from django.db import transaction
from store.models import Order, OrderItem


@transaction.atomic()          # to ensures the creation of all of them
def say_hello(request):
    # CREATING A NEW ORDER
    order = Order()
    order.customer_id = 10
    order.save()

    # CREATING A NEW ODER_ITEM
    item = OrderItem()
    item.order = order
    item.quantity = 1
    item.unit_price = 10
    item.product_id = 1
    item.save()

    return render(request, 'hello.html', {'name': 'Mosh'})
