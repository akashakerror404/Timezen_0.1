from django.shortcuts import render,redirect
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth import authenticate,logout
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from store.models import categ, products
from store.models import products
from store.models import colour 
from store.models import product_image
from adminside.forms import *
from userprofile.models import *
from django.urls import reverse
from django.db.models import Sum
from django.http import JsonResponse
from django.db.models.functions import TruncDate
from datetime import datetime
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponseBadRequest
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from coupon.models import *
from datetime import date
import razorpay
from eshop import settings
from django.core.mail import EmailMessage, send_mail
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.cache import cache_control
from authentication.models import *
from cart.models import *



# Create your views here.
def is_superuser(user):
    return user.is_superuser

def soft_delete_product(request, slug):
    product = get_object_or_404(products, slug=slug)
    product.available = False  # Set 'available' field to False
    product.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def undo_soft_delete_product(request,slug):
    product = get_object_or_404(products, slug=slug)
    product.available = True  # Set 'available' field to False
    product.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def edit_product(request, product_id):
    product = get_object_or_404(products, id=product_id)

    if request.method == 'POST':
        # Handle form submission and update the product fields
        product.name = request.POST['name']
        product.desc = request.POST['desc']
        product.available = bool(request.POST.get('available'))  # Convert to boolean value
        product.price = request.POST['price']
        discountprice = request.POST['discountprice']  # Initialize discountprice with None
        if discountprice == '':
            discountprice = None

        product.discountprice = discountprice  # Assign the value to the product's discountprice field

        product.category_id = request.POST['category']
        product.save()

        return redirect('product_management')

    categories = categ.objects.all()
    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'admin/edit_product.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def create_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount_price = request.POST.get('discount_price', 150)
        minimum_amount = request.POST.get('minimum_amount', 500)
        expiry_date = request.POST.get('expiry_date')

        # Check if the coupon with the same coupon code already exists
        existing_coupon = Coupon.objects.filter(coupon_code=coupon_code).first()
        if existing_coupon:
            # If the coupon already exists, display a flash message
            messages.error(request, 'Coupon with this code already exists.')
            return redirect('create_coupons')

        # If the coupon does not exist, create a new one
        coupon = Coupon.objects.create(
            coupon_code=coupon_code,
            discount_price=discount_price,
            minimum_amount=minimum_amount,
            expiry_date=expiry_date
        )

        # Display a success message using flash message
        messages.success(request, 'Coupon created successfully.')
        return redirect('create_coupons')

    # Update the expiry status of each coupon
    coupons = Coupon.objects.order_by('-id')
    for coupon in coupons:
        coupon.check_expiry_status()  # Update the expiry status of the coupon
        coupon.save()  # Save the changes

    context = {
        'coupons': coupons
    }
    return render(request, 'admin/create_coupon.html', context)








# @cache_control(no_cache=True,must_revalidate=True,no_store=True)
# @login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
# @user_passes_test(is_superuser, login_url='adminside')

#this is also used to userside invoice  doenload so dont add the above login requried
def download_order_pdf(request, order_id):
    # Fetch the order details from the database
    order = Order.objects.get(id=order_id)

    # Generate the PDF content
    template_path = 'admin/downloadpdf.html'  # Create a new template for the PDF content
    context = {'order': order}
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    
    # Create the PDF document
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        # Set the response headers for downloading the PDF
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf"'
        return response

    return HttpResponse('Error generating PDF', status=500)




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def download_order_pdf2(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/downloadpdf.html', {'order': order})



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def download_order_pdf_sales(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's totals
    today_orders = Order.objects.filter(order_date__date=today)
    order_count_today = today_orders.count()
    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Weekly totals
    week_orders = Order.objects.filter(order_date__date__range=[week_ago, today])
    order_count_week = week_orders.count()
    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Monthly totals
    month_orders = Order.objects.filter(order_date__date__range=[month_ago, today])
    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Top selling products
    top_selling_products_today = Orderlist.objects.values('product__products__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_week = Orderlist.objects.filter(order_id__order_date__date__range=[week_ago, today]).values('product__products__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_month = Orderlist.objects.filter(order_id__order_date__date__range=[month_ago, today]).values('product__products__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    context = {
        'order_count_today': order_count_today,
        'total_price_today': total_price_today,
        'order_count_week': order_count_week,
        'total_price_week': total_price_week,
        'order_count_month': order_count_month,
        'total_price_month': total_price_month,
        'top_selling_products_today': top_selling_products_today,
        'top_selling_products_week': top_selling_products_week,
        'top_selling_products_month': top_selling_products_month,
    }

    # Render the HTML content using the 'sales.html' template and the provided context
    html_content = render_to_string('admin/sales.html', context)

    # Set the response content type as 'application/pdf' to indicate that it's a PDF file
    response = HttpResponse(content_type='application/pdf')

    # Set the filename for the downloaded file
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Generate the PDF content from the HTML using xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), response)
    
    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response



#this is for add a product

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_description = request.POST.get('description')
        price = request.POST.get('price')
        discountprice = request.POST.get('discountprice')
        if discountprice == '':
            discountprice = None

        category_id = request.POST.get('category')
        selected_colour= request.POST.get('colour')
        stock=request.POST.get('stock')
        display_img=request.FILES.get('display_image')
        print(display_img) 
        images = request.FILES.getlist('images')  # Use getlist to retrieve multiple files

        # Create a product
        category=categ.objects.get(id=category_id)
        print(category)
        productt=products.objects.create(name=product_name,desc=product_description,category=category,price=price,discountprice=discountprice)

        selected_colour_obj=colour.objects.get(colour=selected_colour)

        variant=productVariant.objects.create(
            products=productt,
            colour=selected_colour_obj,
            stock=stock,
            displayimage=display_img,
        )
        variant.save()


        print("addding doneee")

        for img in images:
            product_image.objects.create(product=variant,image=img)

        return redirect ('product_management')
    else:
        categories = categ.objects.all()
        colours = colour.objects.all()  
        context = {
            'categories': categories,
            'colours': colours,  
    }
    return render(request, 'admin/add_product.html', context)

#this for edit a product variant

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def edit_variant(request, variant_id):
    variant = get_object_or_404(productVariant, pk=variant_id)
    images = product_image.objects.filter(product=variant)
    
    if request.method == 'POST':
        selected_colour = request.POST.get('colour')
        stock = request.POST.get('stock')
        display_img = request.FILES.get('display_image')
        images = request.FILES.getlist('images')

        try:
            selected_colour_obj = colour.objects.get(colour=selected_colour)
        except ObjectDoesNotExist:
            selected_colour_obj = colour.objects.first()
        
        variant.colour = selected_colour_obj
        variant.stock = stock
        variant.displayimage = display_img
        variant.save()

        # Remove existing product images
        product_image.objects.filter(product=variant).delete()

        # Add new product images
        for img in images:
            product_image.objects.create(product=variant, image=img)

        return redirect('product_management')
        
    colours = colour.objects.all()
    context = {
        'variant': variant,
        'images': images,
        'colours': colours
    }
    return render(request, 'admin/variant_edit.html', context)

#this for adding this variant for a product

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def add_variant(request,product_id):
    prodt=products.objects.get(id=product_id)
    if request.method == 'POST':
        stock=request.POST.get('stock')
        color =request.POST.get('colour')
        display_img=request.FILES.get('display_image')
        images = request.FILES.getlist('image')


        colour_obj=colour.objects.get(colour=color)
        color=colour.objects.all()
        context ={
            'prodt':prodt,
            'color' :color
            }
        if productVariant.objects.filter(products=prodt, colour=colour_obj).exists():
            messages.error(request, "Product variant already exists.")

            return render(request,'admin/add_variant.html',context)




        variant =productVariant.objects.create(
            products=prodt,
            colour=colour_obj,
            stock=stock,
            displayimage=display_img,
        )

        for img in images:
            product_image.objects.create(product=variant,image=img)
        return redirect('product_management')

    color=colour.objects.all()
    context ={
        'prodt':prodt,
        'color' :color
        }
    return render(request,'admin/add_variant.html',context)








#this for cancel a order

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')

def cancel_order_admin(request, order_id):
    order = Order.objects.get(id=order_id)
    myuser = order.user
    email=myuser.email
    if order.payment_method == 'CASH_ON_DELIVERY':
        print("it heraeeeeeeeeeeeeeeeeee")
        order.payment_status = 'CANCELLED'
        order.save()
        print("cancelled>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        order_lists = Orderlist.objects.filter(order_id=order)
        for order_list in order_lists:
            product_variant = order_list.product
            quantity = order_list.quantity
            product_variant.stock += quantity  # Increase the stock by the canceled quantity
            product_variant.save()
        

        # Cancel user's order
        user_orders =Orderlist.objects.filter(order_id=order)
        for user_order in user_orders:
            user_order.status = 'CANCELLED'
            user_order.save()
            

       

        return redirect('admin_order_list')

    # Refund the order
    order_lists = Orderlist.objects.filter(order_id=order)
    myuser = order.user
    email=myuser.email
    for order_list in order_lists:
        product_variant = order_list.product
        quantity = order_list.quantity
        product_variant.stock += quantity  # Increase the stock by the canceled quantity
        product_variant.save()
    

    client = razorpay.Client(auth=('rzp_test_MZaMhRtV2louDb', 'dT2bluVIx4ea7S7F9xGh8BVN'))
    refund_response = client.payment.refund(order.payment_id, {'amount': int(order.total_price * 100)})

    if refund_response['status'] == 'processed':
        # Refund successful
        order.payment_status = 'REFUNDED'  # Update the payment status to 'REFUNDED'
        order.save()

        # Cancel user's order
        user_orders =Orderlist.objects.filter(order_id=order)
        for user_order in user_orders:
            user_order.status = 'CANCELLED'
            user_order.save()
        



        return redirect('admin_order_list')
    else:
        # Refund failed or not processed
        print("Refund failed or not processed")

    order.payment_status = 'CANCELLED'
    order.save()
    return redirect('admin_order_list')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')

def update_order_status_admin(request, order_id):
    order = Order.objects.get(id=order_id)
    user = order.user

    reffer = ReferralProgram.objects.order_by('-id')[0]

    userwallet=reffer.userwallet
    referrerdwallet=reffer.referrerdwallet
    print(userwallet)
    print(referrerdwallet)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.payment_status = new_status
        if new_status=="DELIVERED":
            has_completed_order = Order.objects.filter(user=user, payment_status='DELIVERED').exists()
            if not has_completed_order:
                buyer_wallet = Wallet.objects.get(user=user)
                try:
                    referral = Referral.objects.get(user=user)
                    if referral.referred_by:

                        referral_wallet = Wallet.objects.get(user=referral.referred_by)
                        referral_wallet.Wallettotal += referrerdwallet  
                        referral_wallet.save()
                        buyer_wallet.Wallettotal += userwallet
                        buyer_wallet.save()
                    else:
                    
                        print(" ivade yethiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
                except Referral.DoesNotExist:
                    print("Referral does not exist.")

               

        
                # order.payment_status = 'COMPLETED'
                order.save()
                return redirect('order_details_admin', order_id=order_id)


        order.save()
        print("order_____________________done")


        return redirect('order_details_admin', order_id=order_id)

    return redirect('order_details_admin', order_id=order_id)









@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def update_product(request, product_id):
    return render(request, 'admin/update_product.html')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def admin_order_list(request):
    search_query = request.GET.get('search')
    order_list = Order.objects.all().order_by('-id')

    if search_query:
        order_list = order_list.filter(id__icontains=search_query)

    paginator = Paginator(order_list, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    order_list = paginator.get_page(page_number)

    context = {
        'order_list': order_list
    }
    return render(request, 'admin/oreder_list_admin.html', context)





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def order_details_admin(request, order_id):
    print(order_id)
    print("order id doneeeeeeeeeee")
    order = get_object_or_404(Order, id=order_id)

    return render(request, 'admin/order_full_deatil.html', {'order': order})




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def dashboard(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if not start_date and not end_date:
            # Calculate the current date
            current_date = timezone.now().date()

            # Calculate the date 30 days back from the current date
            default_start_date = current_date - timedelta(days=30)
            default_end_date = current_date

            # Convert to string format (YYYY-MM-DD)
            start_date = default_start_date.strftime('%Y-%m-%d')
            end_date = default_end_date.strftime('%Y-%m-%d')

        if start_date and end_date:
            order_count_date = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__time__isnull=True)
            ).exclude(payment_status='CANCELLED').count()

            total_price_date = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__time__isnull=True)
            ).exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            daily_totals = Order.objects.filter(
                Q(order_date__date__gte=start_date, order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__time__isnull=True)
            ).exclude(payment_status='CANCELLED').annotate(date=TruncDate('order_date')).values('date').annotate(total=Sum('total_price')).order_by('date')
            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']
            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)
            recent_orders = Order.objects.order_by('-order_date')[:3]
            top_selling_products = Orderlist.objects.values('product__products__name').annotate(total_quantity=Count('product')).order_by('-total_quantity')[:5]



            categories = categ.objects.all()
            data = []

            for category in categories:
                product_count = products.objects.filter(category=category).count()
                data.append(product_count)

            context = {
                'order_count_date': order_count_date,
                'total_price_date': total_price_date,
                'start_date': start_date,
                'end_date': end_date,
                'daily_totals': daily_totals,
                'order_count': order_count,
                'total_price': total_price,
                'categories': categories,
                'data': data,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'recent_orders': recent_orders,
                'top_selling_products':top_selling_products,


            }

            return render(request, 'admin/admin_dashbord.html', context)

        else:
            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)

            categories = categ.objects.all()
            data = []

            for category in categories:
                product_count = products.objects.filter(category=category).count()
                data.append(product_count)


            recent_orders = Order.objects.order_by('-order_date')[:3]
            top_selling_products = Orderlist.objects.values('product__products__name').annotate(total_quantity=Count('product')).order_by('-total_quantity')[:5]
            

            


            context = {
                'order_count': order_count,
                'total_price': total_price,
                'start_date': start_date,
                'end_date': end_date,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'categories': categories,
                'data': data,
                'recent_orders': recent_orders,
                'top_selling_products':top_selling_products,
            }

            return render(request, 'admin/admin_dashbord.html', context)
    
    return HttpResponseBadRequest("Invalid request method.")


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def admin(request):
    if request.user.is_superuser:
        return redirect('dashboard')
    if request.method =='POST':
        username=request.POST['username']
        password1=request.POST['password']

        user=authenticate(username=username,password=password1)
        name=username



        if user is not None and user.is_superuser:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.error(request,"invalid credentials")
            return redirect('adminside')

    return render(request,'admin/adminlogin.html')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def usertable(request):
    users = User.objects.all().order_by('-id')  # Order users by ID in descending order
    search = request.GET.get('search')

    if search:
        users = users.filter(username__icontains=search)

    paginator = Paginator(users, 10)  # Show 10 users per page
    page = request.GET.get('page')
    users = paginator.get_page(page)

    context = {
        'users': users,
        'search': search,
    }
    return render(request, 'admin/usertable.html', context)



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def block_user(request,user_id):
    print(user_id)
    print("user____________________________id")
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    user.is_active = False
    print("user blockedddddddddddddddddddddd")
    user.save()
    return redirect('usertable')
    

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    user.is_active = True  # Set the user's is_active field to True to unblock the user
    user.save()
    return redirect('usertable')
    

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def add_categ(request):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        categoryoffer = request.POST['categoryoffer']
        if categoryoffer == '':
            categoryoffer = None
        categ_image = request.FILES.get('categ_image')
        categ.objects.create(name=category_name, categoryoffer=categoryoffer, img=categ_image)

        print("save image")
        return redirect('category')

    return redirect('category')
    print("sorry")
def edit_category(request, pk):
    category = get_object_or_404(categ, id=pk)

    if request.method == 'POST':
        # Handle the form submission for editing the category
        # For example, update the category fields and save it
        category_name = request.POST['category_name']
        categoryoffer = request.POST.get('categoryoffer')
        # Update other fields as needed...
        category.name = category_name
        category.categoryoffer = categoryoffer
        category.save()

        # Redirect back to the category list after editing
        return redirect('category')

    context = {
        'category': category,
    }
    return render(request, 'admin/edit_category.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def viewproduct(request, product_id):
    product = get_object_or_404(products, pk=product_id)
    variants = product.productvariant_set.all()
    context = {
        'product': product,
        'variants': variants
    }
    return render(request, 'admin/product_view.html', context)



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')   
def logoutadmin(request):
    if request.user.is_authenticated:
        auth_logout(request)
        print("logout")
    return redirect('adminside')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def category(request):
    categ_list=categ.objects.all()
    context={'categ_list': categ_list}
    return render (request,'admin/category.html',context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='adminside')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='adminside')
def product_management(request):
    product_list = products.objects.all().order_by('-id')

    # Retrieve search query from GET parameters
    search_query = request.GET.get('search')

    if search_query:
        # Filter products based on the search query
        product_list = product_list.filter(name__icontains=search_query)

    paginator = Paginator(product_list, 10)  # Show 10 products per page

    page_number = request.GET.get('page')
    products_list = paginator.get_page(page_number)

    context = {'products_list': products_list}

    return render(request, 'admin/product.html', context)

def add_color(request):
    if request.method == 'POST':
        print("ivade yethi")
        new_color = request.POST['new_color']
        colour.objects.create(colour=new_color)
        return redirect('add_product')
    
    colours = colour.objects.all()

    return render(request, 'admin/select_color.html', {'colours':colours})


def add_referral_program(request):

    referral_programs = ReferralProgram.objects.all()
    no_referral_programs = False
    if not referral_programs:
        no_referral_programs = True

    if request.method == 'POST':
        description = request.POST.get('description', '')
        userwallet = int(request.POST.get('userwallet', 50))
        referrerdwallet = int(request.POST.get('referrerdwallet', 100))

        # Create the referral program with the provided data
        ReferralProgram.objects.create(
            description=description,
            userwallet=userwallet,
            referrerdwallet=referrerdwallet
        )

        # Redirect to a success page or perform other actions
        return redirect('add_referral_program')


    context = {
        'referral_programs': referral_programs,
        'no_referral_programs': no_referral_programs,
    }
    return render(request, 'admin/add_referral_program.html', context)

def edit_referral_program(request, program_id):
    program = ReferralProgram.objects.get(id=program_id)
    

    

    if request.method == 'POST':
        description = request.POST.get('description', '')
        userwallet = int(request.POST.get('userwallet', 50))
        referrerdwallet = int(request.POST.get('referrerdwallet', 100))

        program.description = description
        program.userwallet = userwallet
        program.referrerdwallet = referrerdwallet
        program.save()

        return redirect('add_referral_program')

    context = {'program': program}
    return render(request, 'admin/edit_referral_program.html', context)

def return_order_list(request):
    return_orders = Order.objects.filter(payment_status='RETURN')
    
    context = {
        'return_orders': return_orders
    }
    return render(request, 'admin/returnorders.html', context)

def refund_admin(request, order_id):
    order = Order.objects.get(id=order_id)
    user = order.user
    print(order_id)
    order = Order.objects.get(user=user, id=order_id)
    amount=order.total_price
    print("amound________________")
    print(amount)

    order_lists = Orderlist.objects.filter(order_id=order)

            
    order.payment_status = 'REFUND'
    order.save()
    if order.payment_method == 'CASH_ON_DELIVERY':
        buyer_wallet = Wallet.objects.get(user=user)
        buyer_wallet.Wallettotal += amount
        buyer_wallet.save()
    else:
            # Initiate refund using Razorpay API
        client = razorpay.Client(auth=('rzp_test_MZaMhRtV2louDb', 'dT2bluVIx4ea7S7F9xGh8BVN'))
        refund_response = client.payment.refund(order.payment_id, {'amount': int(order.total_price * 100)})

        if refund_response['status'] == 'processed':
                # Refund successful
            order.payment_status = 'REFUND'  # Update the payment status to 'REFUNDED'
            print(f"Order {order_id} refunded successfully")
        else:
                # Refund failed or not processed
            print("Refund failed or not processed")

    order.save()
    print(f"Order {order_id} deleted")
    return redirect('return_order_list')

def banner(request):
    images = CarouselBanner.objects.all()

    if request.method == 'POST':
        image = request.FILES.get('image')
        CarouselBanner.objects.create(image=image)
        return redirect('banner')
    else:
        return render(request, 'admin/banner.html', {'images': images})

    
def delete_image(request, image_id):
    try:
        image = CarouselBanner.objects.get(pk=image_id)
        image.delete()
    except CarouselBanner.DoesNotExist:
        pass
    return redirect('banner')  # Replace 'add_product' with the URL name of the view containing the existing banners template.
