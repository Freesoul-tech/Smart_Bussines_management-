from django import forms

from .models import LodgeActivity, LodgePackage


class LodgeActivityForm(forms.ModelForm):
    class Meta:
        model = LodgeActivity
        fields = ["name", "description", "price", "is_active"]


class LodgePackageForm(forms.ModelForm):
    class Meta:
        model = LodgePackage
        fields = ["name", "description", "price", "included_activities", "is_active"]
        widgets = {"included_activities": forms.CheckboxSelectMultiple}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business
        if business:
            self.fields["included_activities"].queryset = LodgeActivity.objects.filter(business=business, is_active=True)
