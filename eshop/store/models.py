from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

# Create your models here.
class categ(models.Model):
    name=models.CharField(max_length=250,unique=True)
    slug=models.SlugField(max_length=250,unique=True ,null=True, blank=True)
    categoryoffer=models.IntegerField(null=True, blank=True)
    img = models.ImageField(upload_to='categ', null=True, blank=True)



    class Meta:
        ordering=('name',)
        verbose_name='category'
        verbose_name_plural='categories'

    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_url(self):
        return reverse('prod_cat',args=[self.slug])


    def __str__(self):
        return '{}'.format(self.name)


#product adding 
class products(models.Model):
    name=models.CharField(max_length=150,unique=True)
    desc=models.TextField()
    available=models.BooleanField(default=True)
    price=models.IntegerField()
    discountprice=models.IntegerField(default=True,null=True)
    category=models.ForeignKey(categ,on_delete=models.CASCADE)
    slug=models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('product_detail',kwargs={'slug':self.slug})

    def __str__(self):
        return '{}'.format(self.name)

#Colur adding
class colour(models.Model):
    colour = models.CharField(max_length=10)

    def __str__(self):
        return self.colour
#product arinat adding 
class productVariant(models.Model):
    products=models.ForeignKey(products,on_delete=models.CASCADE)
    colour=models.ForeignKey(colour,on_delete=models.CASCADE)
    stock=models.IntegerField()
    displayimage=models.ImageField(upload_to='product_images')
    slug=models.SlugField(blank=True,unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_str = f"{self.products.name}{self.colour}"
            self.slug = slugify(slug_str)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.slug}{self.colour}'
#adding images multipile images for all varinats
class product_image(models.Model):
    product = models.ForeignKey(productVariant,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images')

    def __str__(self):
        return f'{self.product.products.name}{self.product.colour}'

class CarouselBanner(models.Model):
    image = models.ImageField(upload_to='carousel_images')

    def __str__(self):
        return f'Carousel Banner - {self.id}'