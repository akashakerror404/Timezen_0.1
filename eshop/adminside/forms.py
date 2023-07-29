from django import forms
from store. models import product_image,productVariant,products
from multiupload.fields import MultiFileField


from django import forms
from store.models import products, product_image
from multiupload.fields import MultiFileField



class productform(forms.ModelForm):
    images=MultiFileField(min_num=0,max_num=10,max_file_size=1024*1024*5)

    class Meta:
        model =productVariant
        fields=('products','colour','stock','displayimage')