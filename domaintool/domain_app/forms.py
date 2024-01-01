from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Company, Domain
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()
class UserForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label='User Roles',
    )

    status = forms.BooleanField(
        initial=True,
        required=False,
        label='Active',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = get_user_model()  # Use get_user_model to ensure compatibility with custom user models
        fields = ['email', 'username', 'password1', 'is_admin', 'is_user', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password2')
        self.fields['password1'].help_text = ""    
        

class CompanyForm(forms.ModelForm):
    
    class Meta:
        model = Company
        fields = '__all__'
        labels = {
            'name': 'Company Name',
            'address': 'Company Address',
            'location': 'Company Location',
        }
        

class DomainForm(forms.ModelForm):
    
    class Meta:
        model = Domain
        fields = '__all__'
        labels = {
            'name': 'Domain Name',
            'registration_date': 'Date of Registration',
            'expiry_date': 'Date of Expiry',
            'company': 'Belongs To(Company):'
        }