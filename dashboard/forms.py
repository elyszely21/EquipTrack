from django import forms
from django.forms import inlineformset_factory

from accounts.models import UserProfile
from .models import Equipment, BorrowRequest, BorrowRequestItem, ReturnRecord


class EquipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make image field not required
        self.fields['image'].required = False

    class Meta:
        model = Equipment

        fields = [
            "name",
            "category",
            "description",
            "quantity_total",
            "quantity_available",
            "status",
            "image",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Equipment name"
                }
            ),

            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Category"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Description"
                }
            ),

            "quantity_total": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0
                }
            ),

            "quantity_available": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png"
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        total = cleaned_data.get("quantity_total")

        available = cleaned_data.get("quantity_available")

        if total is not None and available is not None:

            if available > total:

                raise forms.ValidationError(
                    "Available quantity cannot exceed total quantity."
                )

        return cleaned_data


class BorrowRequestItemForm(forms.ModelForm):

    class Meta:
        model = BorrowRequestItem
        fields = ["equipment", "quantity"]

        widgets = {
            "equipment": forms.Select(
                attrs={"class": "form-select"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].queryset = Equipment.objects.filter(
            status=Equipment.STATUS_AVAILABLE,
            quantity_available__gt=0,
        ).order_by("name")
        self.fields["equipment"].empty_label = "— Select Equipment —"

    def clean(self):
        cleaned_data = super().clean()
        equipment = cleaned_data.get("equipment")
        quantity = cleaned_data.get("quantity")

        if equipment and quantity:
            if quantity > equipment.quantity_available:
                raise forms.ValidationError(
                    f"Only {equipment.quantity_available} unit(s) of "
                    f'"{equipment.name}" are available.'
                )

        return cleaned_data


BorrowRequestItemFormSet = inlineformset_factory(
    BorrowRequest,
    BorrowRequestItem,
    form=BorrowRequestItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


class ReturnRecordForm(forms.ModelForm):

    class Meta:
        model = ReturnRecord
        fields = ["borrowed_date", "due_date", "return_date", "condition_notes"]

        widgets = {
            "borrowed_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "return_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "condition_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe the condition of returned equipment...",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        borrowed_date = cleaned_data.get("borrowed_date")
        due_date = cleaned_data.get("due_date")
        return_date = cleaned_data.get("return_date")

        if borrowed_date and due_date and due_date < borrowed_date:
            raise forms.ValidationError(
                "Due date cannot be earlier than borrowed date."
            )

        if borrowed_date and return_date and return_date < borrowed_date:
            raise forms.ValidationError(
                "Return date cannot be earlier than borrowed date."
            )

        return cleaned_data


class EditProfileForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = UserProfile
        fields = [
            "middle_name",
            "suffix",
            "contact_number",
            "department",
            "position",
            "profile_picture",
        ]
        widgets = {
            "middle_name": forms.TextInput(attrs={"class": "form-control"}),
            "suffix": forms.TextInput(attrs={"class": "form-control"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
