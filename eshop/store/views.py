from django.shortcuts import render,get_object_or_404
from .models import *
from cart.models import*
from itertools import zip_longest
from django.db.models import Q
from django.core.paginator import Paginator
from .models import categ, products, colour
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.cache import cache_control,never_cache


# Create your views here.
from django.core.paginator import Paginator

def product_detail(request, slug):
    product = productVariant.objects.get(slug=slug)
    producttable = products.objects.get(slug=product.products.slug)
    related_products = products.objects.filter(category=producttable.category).exclude(slug=producttable.slug)[:10]
    context = {
        'product': product,
        'producttable': producttable,
        'related_products': related_products,
    }
    return render(request, 'store/product_details.html', context)

#home landing page
@cache_control(no_store=True,no_cache=True,must_revalidate=True)
def home(request, c_slug=None):
    prodt = products.objects.filter(available=True).order_by('-id')[:10]  # Retrieve latest 10 available products
    paginator = Paginator(prodt, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    cat = categ.objects.all()
    categories_with_offers = categ.objects.filter(categoryoffer__isnull=False)  # Retrieve all categories with offers
    carousel_banners = CarouselBanner.objects.all()
    zipped_data = zip_longest(categories_with_offers, carousel_banners)
    product = productVariant.objects.all()
    user = request.user
    if user.is_authenticated:
        cart_count = Cart.objects.filter(cart_id__user=user).count()
        wish_count = Wish.objects.filter(wish_id__user=user).count()
    else:
        cart_count = 0
        wish_count = 0
    context = {
        'page_obj': page_obj,
        'ct': cat,
        'product': product,
        'cart_count': cart_count,
        'wish_count': wish_count,
        'user': user,
        'categories_with_offers': categories_with_offers,  # Pass the categories with offers to the template
        'carousel_banners': carousel_banners,
        'zipped_data': zipped_data,
        }
    return render(request, 'home.html',context)

#shop page bellow filter option maily
def shop(request):
    categories = categ.objects.all()
    selected_category = request.GET.get('category', '')
    selected_color = request.GET.get('color', '')
    selected_price = request.GET.get('price', '')
    search_query = request.GET.get('search', '')  # Get the search query from the URL parameter
    prodt = products.objects.filter(available=True)
    if selected_category:
        prodt = prodt.filter(category__slug=selected_category)
    if selected_color:
        prodt = prodt.filter(productvariant__colour__id=selected_color)
    if selected_price == '500-1000':
        prodt = prodt.filter(Q(price__range=(500, 1000)) | Q(discountprice__range=(500, 1000)))
    elif selected_price == '1000-2000':
        prodt = prodt.filter(Q(price__range=(1000, 2000)) | Q(discountprice__range=(1000, 2000)))
    elif selected_price == '2000-3000':
        prodt = prodt.filter(Q(price__range=(2000, 3000)) | Q(discountprice__range=(2000, 3000)))
    if search_query:
        prodt = prodt.filter(name__icontains=search_query)  # Filter products based on search query
    colours = colour.objects.all()
    # Get the categories with category offers
    categories_with_offer = [category for category in categories if category.categoryoffer]
    if categories_with_offer:
        # Get all products that belong to categories with category offers
        prodt = prodt.filter(category__in=categories_with_offer)

    paginator = Paginator(prodt, 12)  # Display 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'prodt': page_obj,
        'colours': colours,
        'selected_category': selected_category,
        'selected_color': selected_color,
        'selected_price': selected_price,
        'search_query': search_query,  # Pass the search query to the template
        'has_category_offer': len(categories_with_offer) > 0,
        'max_offer_category': max(categories_with_offer, key=lambda category: category.categoryoffer, default=None),
    }
    return render(request, 'shop.html', context)


def error(request):
    return render(request, 'error404.html')

    


