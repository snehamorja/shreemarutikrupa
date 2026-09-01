from django import forms
from django.contrib.auth.models import User
from core.models import ScaifeEntry, Office, PricingConfig, UserProfile, BrandingSettings, Inquiry, WorkerProfile, WorkerFinancialEntry

class ScaifeEntryForm(forms.ModelForm):
    class Meta:
        model = ScaifeEntry
        fields = [
            'quantity',
            'service_lapping', 'service_coating', 'service_diamond_scaife',
            'quantity_lapping', 'quantity_coating', 'quantity_diamond',
            'cost', 'needs_repair', 'repair_details', 'notes'
        ]
        labels = {
            'quantity': 'Total Quantity of Scaifes',
            'quantity_lapping': 'Lapping Scaifes Count',
            'quantity_coating': 'Coating Scaifes Count',
            'quantity_diamond': 'Diamond Scaife Count',
            'service_lapping': 'Lapping Service',
            'service_coating': 'Coating Service',
            'service_diamond_scaife': 'Diamond Scaife Service',
            'needs_repair': 'Send to Repair / Needs Repair',
            'repair_details': 'Repair Details / Remarks',
        }


class OfficeForm(forms.ModelForm):
    manager_username = forms.CharField(
        max_length=150,
        required=False,
        label="Manager Login Username",
        widget=forms.TextInput(attrs={'placeholder': 'E.g. surat_manager (or leave blank to auto-generate)'}),
        help_text="Custom login username for the office manager account"
    )
    manager_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter manager password (or leave blank to auto-generate)'}),
        required=False,
        label="Manager Login Password",
        help_text="Custom login password for the office manager account"
    )

    class Meta:
        model = Office
        fields = ['name', 'location', 'phone', 'email', 'manager_username', 'manager_whatsapp']
        labels = {
            'manager_whatsapp': "Manager's WhatsApp Number (with country code, e.g. 919876543210)",
        }


class PricingConfigForm(forms.ModelForm):
    class Meta:
        model = PricingConfig
        fields = ['lapping_rate', 'coating_rate', 'diamond_scaife_rate']


class BrandingSettingsForm(forms.ModelForm):
    class Meta:
        model = BrandingSettings
        exclude = []  # Include all fields
        widgets = {
            'google_map_embed': forms.TextInput(attrs={'placeholder': 'Iframe source URL'}),
        }


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'phone', 'subject', 'message']


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial='worker')
    office = forms.ModelChoiceField(queryset=Office.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            profile = user.profile
            profile.role = self.cleaned_data["role"]
            profile.office = self.cleaned_data["office"]
            profile.save()
        return user


class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    office = forms.ModelChoiceField(queryset=Office.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            profile = self.instance.profile
            self.fields['role'].initial = profile.role
            self.fields['office'].initial = profile.office

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.role = self.cleaned_data["role"]
            profile.office = self.cleaned_data["office"]
            profile.save()
        return user


class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ['name', 'phone', 'email', 'base_salary', 'joining_date', 'notes', 'is_active']
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
        }


class WorkerFinancialEntryForm(forms.ModelForm):
    class Meta:
        model = WorkerFinancialEntry
        fields = ['entry_type', 'amount', 'leave_days', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
