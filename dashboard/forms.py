from django import forms
from .models import Equipment


class EquipmentForm(forms.ModelForm):

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
                    "accept": "image/jpeg,image/png,image/gif,image/webp"
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