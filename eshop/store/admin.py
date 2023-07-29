from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(categ)
admin.site.register(products)
admin.site.register(colour)
admin.site.register(productVariant)
admin.site.register(product_image)
admin.site.register(CarouselBanner)




class ProductImageAdmin(admin.StackedInline):
    model = product_image


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]

# admin.site.register(products, ProductAdmin)
# admin.site.register(product_image)