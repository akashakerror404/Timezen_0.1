from django import template
from cart.models import *

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_items_count(context):
    user = context['request'].user
    cart_items_count = Cart.objects.filter(cart_id__user=user).count()
    return cart_items_count

@register.simple_tag(takes_context=True)
def wish_list_count(context):
    user = context['request'].user
    wish_list_count = Wish.objects.filter(wish_id__user=user).count()
    return  wish_list_count