from django.shortcuts import render
from django.shortcuts import render, redirect 
from store.models import *
from coupon.models import *
from.models import *
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Sum
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control,never_cache
from django.views.decorators.cache import cache_control



# Create your views here.
@login_required(login_url='signin')
def add_to_cart(request, slug):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        product = productVariant.objects.get(slug=slug)
        productvariant = products.objects.get(slug=product.products.slug)
        user = request.user
        if productvariant.discountprice:
            price = Decimal(productvariant.discountprice)
        
        else:
            price = Decimal(productvariant.price)

        if productvariant.category.categoryoffer:
            discount=price*productvariant.category.categoryoffer/100
            price -= discount
            price = round(price, 0)
        else:
            if productvariant.discountprice:
                price = Decimal(productvariant.discountprice)
            else:
                price = Decimal(productvariant.price)
        totalprice = price * Decimal(quantity)
        # totalprice = price * Decimal(quantity)

        try:
            cart = UserCart.objects.get(user=user)
            cart_item = Cart.objects.filter(cart_id=cart, product=product).first()

            if cart_item:
                # Product already exists in cart, increase the quantity
                cart_item.quantity = F('quantity') + int(quantity)
                cart_item.price = F('price') + totalprice
                cart_item.save()
            else:
                # Product does not exist in cart, create a new cart item
                Cart.objects.create(cart_id=cart, product=product, quantity=quantity, price=totalprice)
                messages.success(request, "iteam has been added to your cart.")

        except UserCart.DoesNotExist:
            cart = UserCart.objects.create(user=user)
            Cart.objects.create(cart_id=cart, product=product, quantity=quantity, price=totalprice)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'cart/cart.html')
@login_required(login_url='signin')   
def add_to_wish(request, slug):
    if request.method == 'POST':
        product = productVariant.objects.get(slug=slug)
        productvariant = products.objects.get(slug=product.products.slug)
        user = request.user
        
        if productvariant.discountprice:
            price = Decimal(productvariant.discountprice)
        
        else:
            price = Decimal(productvariant.price)

        if productvariant.category.categoryoffer:
            discount=price*productvariant.category.categoryoffer/100
            price -= discount
            price = round(price, 0)
        
        else:
            if productvariant.discountprice:
                price = Decimal(productvariant.discountprice)
            else:
                price = Decimal(productvariant.price)
        # totalprice = price * Decimal(quantity)
        totalprice = price

        try:
            wish = UserWish.objects.get(user=user)
            wish_item = Wish.objects.filter(wish_id=wish, product=product).first()

            if wish_item:
                # Product already exists in wishlist
                messages.info(request, "This product is already in your wishlist.")
            else:
                # Product does not exist in wishlist, create a new wishlist item
                Wish.objects.create(wish_id=wish, product=product, quantity=1, price=totalprice)
                messages.success(request, "Product added to your wishlist successfully.")
        except UserWish.DoesNotExist:
            wish = UserWish.objects.create(user=user)
            Wish.objects.create(wish_id=wish, product=product, quantity=1, price=totalprice)
            messages.success(request, "Product added to your wishlist successfully.")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'cart/wish.html')


@login_required(login_url='signin')

def wish_list(request):
    user = request.user
    user_wish = UserWish.objects.get(user=user)
    products = Wish.objects.filter(wish_id=user_wish)
    if products :

        productstotal = Wish.objects.filter(wish_id=user_wish).aggregate(total_price=Sum('price'))
        total_price = productstotal['total_price']

        context = {
            'products': products,
            'total_price': total_price
        }
        return render(request, 'cart/wish.html', context)
    else:
        messages.info(request, "Your Wish is empty!")

        return redirect('shop')

@login_required(login_url='signin')  # Add the login_required decorator to restrict access
@cache_control(no_store=True,no_cache=True,must_revalidate=True)
def cart(request):
    user = request.user
    cart_id = UserCart.objects.get(user=user)
    cart_item = Cart.objects.filter(cart_id = cart_id)
    if cart_item :


        user = request.user
        cart_id = UserCart.objects.get(user=user)
        products = Cart.objects.filter(cart_id=cart_id)
        productstotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
        total_price = productstotal['total_price']
        subtotal = Cart.objects.filter(cart_id=cart_id).aggregate(total_price=Sum('price'))
        subtotal=subtotal['total_price']
        has_category_offer = False
        for cart_item in products:
            product = cart_item.product
            category = product.products.category  # Access category through the products model
            if category.categoryoffer:
                has_category_offer = True
                break
        coupon_status = None  # Assign a default value to coupon_status
        discount = 0  # Assign a default value to discount

        if request.method == 'POST':
            coupon_code = request.POST.get('coupon')
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code, is_expired=False, minimum_amount__lte=total_price)

                # Add a new condition to check if the user has already applied the coupon
                user_coupon = Usercoupon.objects.filter(user=user, coupon=coupon.id).first()
                if user_coupon is None:
                    # User has not already applied the coupon
                    cart_id.coupons = coupon
                    cart_id.save()
                    discount = coupon.discount_price
                    total_price -= coupon.discount_price
                else:
                    coupon_status = 'already_used'  # Set the coupon status as 'already_used'
                    # User has already applied the coupon
                    # Handle this case as per your requirements
                
            except Coupon.DoesNotExist:
                coupon_status = 'invalid'  # Set the coupon status as 'invalid'
                # Coupon not valid

        context = {
            'products': products,
            'total_price': total_price,
            'coupon_status': coupon_status,  # Add the coupon status to the context
            'discount': discount,
            'subtotal':subtotal,
            'has_category_offer': has_category_offer,
            

        }
        return render(request, 'cart/cart.html', context)
    else:
        messages.info(request, "Your cart is empty!")

        return redirect('shop')




def quantity_update(request, slug):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        product = productVariant.objects.get(slug=slug)
        productvariant = products.objects.get(slug=product.products.slug)
        user = request.user
        
        if productvariant.discountprice:
            price = Decimal(productvariant.discountprice)
        
        else:
            price = Decimal(productvariant.price)

        if productvariant.category.categoryoffer:
            discount=price*productvariant.category.categoryoffer/100
            price -= discount
            price = round(price, 0)
        
        else:
            if productvariant.discountprice:
                price = Decimal(productvariant.discountprice)
            else:
                price = Decimal(productvariant.price)
        totalprice = price * Decimal(quantity)
        if quantity <= product.stock:
            try:
                cart = UserCart.objects.get(user=user)
            except UserCart.DoesNotExist:
                cart = UserCart.objects.create(user=user)

            cart_item, created = Cart.objects.get_or_create(cart_id=cart, product=product)
            cart_item.quantity = quantity
            cart_item.price = totalprice
            cart_item.save()
        return redirect('cart')
# deleteing product from cart

def delete_cart(request, product_id):
    user = request.user #geting the  user

    try:
        cart = UserCart.objects.get(user=user)
        cart_items = Cart.objects.filter(cart_id=cart, product_id=product_id)
        
        for cart_item in cart_items:
            cart_item.delete()
    except (UserCart.DoesNotExist, Cart.DoesNotExist):
        pass

    return redirect('cart')  # rediract cart

def delete(request, product_id):
    user = request.user #geting the  user

    try:
        wish = UserWish.objects.get(user=user)
        wish_items = Wish.objects.filter(wish_id=wish, product_id=product_id)
        
        for wish_item in wish_items:
            wish_item.delete()
        
    except (UserWart.DoesNotExist, Wart.DoesNotExist):
        pass

    return redirect('wish_list')  # rediract cart

