from django import forms
from .models import User, UserProfile
from . validators import allow_only_images_validator

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']

    
    #overriding the clean_data method to use a custom validation to check if the passwords match
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("The two passwords do not match!")

class UserProfileForm(forms.ModelForm):
    #added this when i changed addre 1and 2 to addr
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'start typing...', 'required':'required'}))
    #styling the file selector
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])

    #making the latitude and longitude fields readonly
    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))

    #alternatively you can use this to set the field readonly

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'postal_code', 'country', 'province', 'city', 'latitude', 'longitude']


# I created this form to be used to update the user infor such as firstname, lastname, telephone
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','phone_number']