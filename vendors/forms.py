from django import forms
from .models import Vendor

class VendorForm(forms.ModelForm):
    #styling the file input
    vendor_license = forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}))
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']

    
   