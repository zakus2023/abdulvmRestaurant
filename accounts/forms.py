from django import forms
from .models import User, UserProfile

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
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}))
    cover_photo = forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}))
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address_line_1', 'address_line_2', 'postal_code', 'country', 'province', 'city', 'latitude', 'longitude']