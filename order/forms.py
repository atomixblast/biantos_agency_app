from django import forms

from biantos_agency.utilities.ui_consts import INPUT_FLOAT_FIELD
from order.models import Order




class AddOrderForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make json_repr not required in form validation (will be populated by JS)
        self.fields['json_repr'].required = False
        # Remise sur la commande : optionnelle, 0 si vide
        self.fields['global_discount'].required = False
        self.fields['global_discount_type'].required = False

    def clean_global_discount(self):
        return self.cleaned_data.get('global_discount') or 0

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('global_discount_type'):
            cleaned['global_discount_type'] = Order.DISCOUNT_PERCENT
        if cleaned['global_discount_type'] == Order.DISCOUNT_PERCENT and (cleaned.get('global_discount') or 0) > 100:
            self.add_error('global_discount', "Une remise en pourcentage ne peut pas dépasser 100 %.")
        return cleaned

    class Meta:
        model = Order
        fields = ['name', 'ordered_at', 'state', 'sales_executive', 'customer', 'global_discount', 'global_discount_type', 'json_repr']

        widgets = {
            'name': forms.TextInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Nommer la commande'}),
            'cashed': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Montant encaissé'}),
            'discount': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Montant de la reduction'}),
            'ordered_at': forms.DateInput(attrs={'type': 'date', 'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez la date de la commande'}),
            'sales_executive': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez le nom de l\'apporteur d\'affaire'}),
            'customer': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Choisissez un client'}),
            'state': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Etat de la commande'}),
            'global_discount': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'min': '0', 'step': 'any', 'placeholder': '0', 'x-model.number': 'discount'}),
            'global_discount_type': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-8 block border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary", 'x-model': 'discountType', 'aria-label': 'Type de remise'}),
            'json_repr': forms.HiddenInput(),
        }

        labels = {
            'name': 'Désignation de la commande',
            'cashed': 'Montant encaissé',
            'discount': 'Remise',
            'ordered_at': 'Date de la commande',
            'sales_executive': 'Apporteur d\'affaire',
            'customer': 'Client',
            'state': 'Statut de la commande',
            'global_discount': 'Remise sur la commande',
            'global_discount_type': 'Type de remise',
        }


class UpdateOrderForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make json_repr not required in form validation (will be populated by JS)
        self.fields['json_repr'].required = False
        # Remise sur la commande : optionnelle, 0 si vide
        self.fields['global_discount'].required = False
        self.fields['global_discount_type'].required = False

    def clean_global_discount(self):
        return self.cleaned_data.get('global_discount') or 0

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('global_discount_type'):
            cleaned['global_discount_type'] = Order.DISCOUNT_PERCENT
        if cleaned['global_discount_type'] == Order.DISCOUNT_PERCENT and (cleaned.get('global_discount') or 0) > 100:
            self.add_error('global_discount', "Une remise en pourcentage ne peut pas dépasser 100 %.")
        return cleaned

    class Meta:
        model = Order
        fields = ['name', 'ordered_at', 'state', 'sales_executive', 'customer', 'global_discount', 'global_discount_type', 'json_repr']

        widgets = {
            'name': forms.TextInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Nommer la commande'}),
            'ordered_at': forms.DateInput(attrs={'type': 'date', 'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez la date de la commande'}),
            'discount': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Montant de la reduction'}),
            'ordered_at': forms.DateInput(attrs={'type': 'date', 'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez la date de la commande'}),
            'sales_executive': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez le nom de l\'apporteur d\'affaire'}),
            'customer': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Choisissez un client'}),
            'state': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Etat de la commande'}),
            'global_discount': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'min': '0', 'step': 'any', 'placeholder': '0', 'x-model.number': 'discount'}),
            'global_discount_type': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-8 block border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary", 'x-model': 'discountType', 'aria-label': 'Type de remise'}),
            'json_repr': forms.HiddenInput(),
        }

        labels = {
            'name': 'Désignation de la commande',
            'cashed': 'Montant encaissé',
            'discount': 'Remise',
            'ordered_at': 'Date de la commande',
            'sales_executive': 'Apporteur d\'affaire',
            'customer': 'Client',
            'state': 'Statut de la commande',
            'global_discount': 'Remise sur la commande',
            'global_discount_type': 'Type de remise',
        }