from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Vendor, Organization, Tender, Bid, Clarification


class StyledFormMixin:
    """Mixin to add Bootstrap form-control class to all fields"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class UserRegistrationForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name",
            "email", "password1", "password2"
        ]


class VendorRegistrationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Vendor
        exclude = ["id", "slug", "is_verified", "is_blacklisted",
                   "rating", "total_reviews", "created_at", "updated_at", "user"]


class OrganizationRegistrationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ["id", "slug", "is_verified", "created_at", "updated_at"]


class TenderForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Tender
        exclude = ["id", "slug", "views_count", "is_featured",
                   "created_by", "created_at", "updated_at"]


class BidForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Bid
        exclude = ["id", "slug", "status", "technical_score", "financial_score",
                   "total_score", "evaluator_comments", "submitted_at",
                   "reviewed_at", "created_at", "updated_at"]


class ClarificationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Clarification
        exclude = ["id", "answer", "is_answered", "answered_at",
                   "asked_at", "is_public"]
