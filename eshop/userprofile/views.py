from django.shortcuts import render
from.models import *
from django.shortcuts import render, redirect, get_object_or_404
from userprofile.models import Address
from cart.models import Cart,UserCart
from decimal import Decimal
from django.db.models import Sum
from datetime import timedelta
from django.contrib.auth.models import User
from django.conf import settings
import razorpay
from django.http import JsonResponse
from coupon.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.paginator import Paginator
from eshop import settings
from django.core.mail import EmailMessage, send_mail
from django.core.mail import send_mail
from authentication.models import *
from cart.models import *
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_control,never_cache
from django.views.decorators.cache import cache_control
from django.db.models import Sum


def add_address(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        country = request.POST.get('country')
        address = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        state = request.POST.get('state')
        # Create a new Address instance and save it
        address_obj = Address(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            country=country,
            address=address,
            city=city,
            pincode=pincode,
            phone=phone,
            email=email,
            state=state
        )
        address_obj.save()
        return redirect('adress_selection')
    else :
        return render (request,'userprofile/add_adress.html')

        

@login_required(login_url='signin') 
@cache_control(no_store=True,no_cache=True,must_revalidate=True)
def adress_selection(request):
    user = request.user
    cart_id = UserCart.objects.get(user=user)
    cart_iteam=Cart.objects.filter(cart_id=cart_id)
    if cart_iteam:
        cart_items = Cart.objects.filter(cart_id=cart_id)
        cart_total = cart_items.aggregate(total_price=Sum('price'))['total_price']
        cart_count = cart_items.exists()
        if cart_count:
            addresses = Address.objects.filter(user=user)
            context = {
                'addresses': addresses,
                'cart_total': cart_total,
                'cart_items': cart_items,
            }
            return render(request, 'userprofile/adress.html', context)
        else:
            return redirect('shop')
    else:
        return redirect('shop')

@login_required(login_url='signin') 
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        # Retrieve updated address data from the form
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        country = request.POST.get('country')
        address_text = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        state = request.POST.get('state')

        # Update the address object with the new data
        address.first_name = first_name
        address.last_name = last_name
        address.country = country
        address.address = address_text
        address.city = city
        address.pincode = pincode
        address.phone = phone
        address.email = email
        address.state = state
        address.save()
        return redirect('adress_selection')  # Redirect to the address view or any other appropriate page
    else:
        pass

        return render(request, 'userprofile/edit_adress.html',{'address':address})

def payment_page(request,address_id):
    address=Address.objects.get
    user=request.user
    cart_id=UserCart.objects.ge(user=user)
    products=Cart.objects.filter(cart_id=cart_id)
    producttotal=Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
    return render(request,'pyment.html')

@login_required(login_url='signin') 
def initiate_payment(request):
    amount = request.POST.get('total_price')
    amount = int(float(amount))
    order_amount = amount * 100
    order_currency = 'INR'
    order_receipt = 'order_receipt'
    note = {'shipping_address': '123, shipping Street'}
    import razorpay

    client = razorpay.Client(auth=('rzp_test_MZaMhRtV2louDb', 'dT2bluVIx4ea7S7F9xGh8BVN'))

    razorpay_order = client.order.create(
        {'amount': order_amount,
         'currency': order_currency,
         'receipt': order_receipt,
         'payment_capture': 1}  # Set payment_capture to 0 for manual capture
    )
    razorpay_order_id = razorpay_order['id']
    amount = razorpay_order['amount']
    return JsonResponse({'razorpay order id': razorpay_order_id, 'amount': amount})

@login_required(login_url='signin')
@cache_control(no_store=True,no_cache=True,must_revalidate=True)
def place_order(request,address_id):
    user=request.user
    cart = UserCart.objects.get(user = request.user)
    cart_iteam=Cart.objects.filter(cart_id=cart)
    if cart_iteam:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        cart_id=UserCart.objects.get(user=user)
        buyer_wallet = Wallet.objects.get(user=user)
        wallet_total = buyer_wallet.Wallettotal
        productstotal=Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
        subtotal_price=productstotal['total_price']
        if cart_id.coupons :
            discount_price = cart_id.coupons.discount_price if cart_id.coupons else 0  # Check if a coupon exists and get the discount price, otherwise set it to 0
            total_price = int(subtotal_price - discount_price) if cart_id.coupons else subtotal_price

        else:
            total_price = subtotal_price
        context = {
            'subtotal_price':subtotal_price,
            'address': address,
            'total_price':total_price,
            'wallet_total': wallet_total,

        }
        return render(request, 'userprofile/order_summary.html', context)
    else:
        return redirect('shop')

    
@login_required(login_url='signin')
@cache_control(no_store=True,no_cache=True,must_revalidate=True)
def order_placed(request,address_id):
    address=Address.objects.get(id=address_id)
    user=request.user
    cart_id=UserCart.objects.get(user=user)
    producttotal=Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
    subtotal_price=producttotal['total_price']
    if cart_id.coupons :
        discount_price = cart_id.coupons.discount_price if cart_id.coupons else 0  # Check if a coupon exists and get the discount price, otherwise set it to 0
        total_price = int(subtotal_price - discount_price) if cart_id.coupons else subtotal_price

    else:
        total_price = subtotal_price
    order=Order.objects.create(
        user=user,
        address=address,
        total_price=total_price,
        payment_status='ORDERED',
        payment_method='CASH_ON_DELIVERY'
        )
    cart_item=Cart.objects.filter(cart_id=cart_id)
    for product in cart_item:
        Orderlist.objects.create(order_id=order,
                                product=product.product,
                                quantity=product.quantity,
                                price=product.price)
        
        varinat=product.product
        varinat.stock -=product.quantity
        varinat.save()
        


         # Decrease the stock by the ordered quantity                      
        product.delete()
        if cart_id.coupons:
            user_coupon = Usercoupon.objects.create(user=user,coupon=cart_id.coupons,total_price=total_price)
        
        cart_id.coupons = None  # Set the coupons field to NULL
        cart_id.save()
        
    context={
        'order':order,
        'order_id': order.id

    }
    return JsonResponse({'order_id': order.id})
    
@login_required(login_url='signin') 
def order_wallet(request,address_id):
    address=Address.objects.get(id=address_id)
    user=request.user
    cart_id=UserCart.objects.get(user=user)
    producttotal=Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
    subtotal_price=producttotal['total_price']
    if cart_id.coupons :
        discount_price = cart_id.coupons.discount_price if cart_id.coupons else 0  # Check if a coupon exists and get the discount price, otherwise set it to 0
        total_price = int(subtotal_price - discount_price) if cart_id.coupons else subtotal_price
    else:
        total_price = subtotal_price
    order=Order.objects.create(
        user=user,
        address=address,
        total_price=total_price,
        payment_status='ORDERED',
        payment_method='WALLET'
        )
    buyer_wallet = Wallet.objects.get(user=user)
    buyer_wallet.Wallettotal -= total_price
    buyer_wallet.save()
    cart_item=Cart.objects.filter(cart_id=cart_id)
    for product in cart_item:
        Orderlist.objects.create(order_id=order,
                                product=product.product,
                                quantity=product.quantity,
                                price=product.price)
        
        varinat=product.product
        varinat.stock -=product.quantity
        varinat.save()
        product.delete()
        if cart_id.coupons:
            user_coupon = Usercoupon.objects.create(user=user,coupon=cart_id.coupons,total_price=total_price)
        cart_id.coupons = None  # Set the coupons field to NULL
        cart_id.save()
    context={
        'order':order,
        'order_id': order.id

    }
    return render(request,'userprofile/orderinvoice.html',context)

@login_required(login_url='signin') 
def order_placed_razopay(request, address_id):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        address = Address.objects.get(id=address_id)
        user = request.user
        cart_id = UserCart.objects.get(user=user)
        producttotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
        subtotal_price = producttotal['total_price']

        if cart_id.coupons:
            discount_price = cart_id.coupons.discount_price if cart_id.coupons else 0
            total_price = int(subtotal_price - discount_price) if cart_id.coupons else subtotal_price
        else:
            total_price = subtotal_price
        order = Order.objects.create(
            user=user,
            address=address,
            total_price=total_price,
            payment_status='ORDERED',  # Set the payment status to 'CAPTURED'
            payment_method='PREPAID',
            payment_id=payment_id
        )

        # Capture the payment using Razorpay API
        client = razorpay.Client(auth=('rzp_test_MZaMhRtV2louDb', 'dT2bluVIx4ea7S7F9xGh8BVN'))
        capture_response = client.payment.capture(payment_id, float(total_price) * 100)  # Capture the payment amount
        cart_items = Cart.objects.filter(cart_id=cart_id)

        for product in cart_items:
            Orderlist.objects.create(
                order_id=order,
                product=product.product,
                quantity=product.quantity,
                price=product.price
            )

            variant = product.product
            variant.stock -= product.quantity
            variant.save()
           

            product.delete() # deleate the product frim cart

        if cart_id.coupons:
            user_coupon = Usercoupon.objects.create(user=user, coupon=cart_id.coupons, total_price=total_price)
            cart_id.coupons = None  # Set the coupons field to NULL
            cart_id.save()

        return JsonResponse({'order_id': order.id})
    else:
        return JsonResponse({'error': 'Invalid request method'})


@cache_control(private=True, no_store=True, no_cache=True, must_revalidate=True)
@login_required(login_url='signin')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order
    }
    return render(request, 'userprofile/order_confirmation.html', context)



@login_required(login_url='signin') 
def user_orders_list(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-id')  # Retrieve all orders for the current user, ordered by ID in descending order
    paginator = Paginator(orders, 5)  # Display 10 orders per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
    }
    return render(request, 'userprofile/user_orders_list.html', context)


def delete_order(request, order_id):
    user = request.user


    try:
        order = Order.objects.get(user=user, id=order_id)
        amount=order.total_price

        order_lists = Orderlist.objects.filter(order_id=order)

        for order_list in order_lists:
            product_variant = order_list.product
            quantity = order_list.quantity
            product_variant.stock += quantity  # Increase the stock by the canceled quantity
            product_variant.save()

        if order.payment_method == 'CASH_ON_DELIVERY':
            # No refund needed for cash on delivery orders
            order.payment_status = 'CANCELLED'

        elif order.payment_method == 'WALLET':
            buyer_wallet = Wallet.objects.get(user=user)
            buyer_wallet.Wallettotal += amount
            buyer_wallet.save()
            order.payment_status = 'REFUNDED'


        else:
            # Initiate refund using Razorpay API
            client = razorpay.Client(auth=('rzp_test_MZaMhRtV2louDb', 'dT2bluVIx4ea7S7F9xGh8BVN'))
            refund_response = client.payment.refund(order.payment_id, {'amount': int(order.total_price * 100)})

            if refund_response['status'] == 'processed':
                # Refund successful
                order.payment_status = 'REFUNDED'  # Update the payment status to 'REFUNDED'
            else:
                # Refund failed or not processed
                pass

        order.save()

    except Order.DoesNotExist:
        pass

    return redirect('user_orders_list')

@login_required(login_url='signin') 
def refund_method(request, order_id):
    user = request.user
   

    try:
        order = Order.objects.get(user=user, id=order_id)
        amount=order.total_price
        order_lists = Orderlist.objects.filter(order_id=order)

        for order_list in order_lists:
            product_variant = order_list.product
            quantity = order_list.quantity
            product_variant.stock += quantity  # Increase the stock by the canceled quantity
            product_variant.save()
            order.payment_status = 'RETURN'
            order.save()
    except Order.DoesNotExist:
        pass

    return redirect('user_orders_list')


@login_required(login_url='signin') 
def view_order_details(request, order_id):
    # Retrieve the order details based on the order_id
    order = Order.objects.get(id=order_id)
    context = {
        'order': order,
        }
    
    # Pass the order object to the template
    return render(request, 'userprofile/orderinvoice.html', context)


@login_required(login_url='signin') 
def userprofile(request):
    user = request.user
    try:
        referral=Referral.objects.get(user=user)
    except Referral.DoesNotExist:
        referral = None
    try:
        personal_details = PersonalDetails.objects.get(user=user)
    except PersonalDetails.DoesNotExist:
        personal_details = None


    context = {
        'username': user.username,
        'email': user.email,
        'referral': referral,
        'personal_details': personal_details,  # Include the PersonalDetails object in the context

        }
    return render(request, 'userprofile/userprofile.html',context)


@login_required(login_url='signin') 
def wallet(request):
    user = request.user
    reffer = ReferralProgram.objects.order_by('-id')[0]
    description=reffer.description


    try:
        referral = Referral.objects.get(user=user)
    except Referral.DoesNotExist:
        referral = None
    try:
        wallet_amount = Wallet.objects.get(user=user).Wallet_total()  # Correct method name
    except Wallet.DoesNotExist:
        wallet_amount = None

    context = {
        'username': user.username,
        'email': user.email,  # Pass the email to the context if needed
        'referral': referral,
        'wallet_amount': wallet_amount,
        'description':description,
        }
    return render(request, 'userprofile/wallet.html', context)



@login_required(login_url='signin') 
def update_profile(request):
    profile = PersonalDetails.objects.get(user = request.user)
    if request.method == 'POST' and request.FILES.get('image'):
        profile_image = request.FILES['image']

        profile.profile_picture = profile_image
        profile.save()
        data = {
            
        }
        return JsonResponse({'message': 'Image uploaded successfully!'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
        
def help(request):
    return render(request,'userprofile/help.html')