from django import forms

from biantos_agency.utilities.ui_consts import INPUT_FLOAT_FIELD
from order.models import Order




class AddOrderForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make json_repr not required in form validation (will be populated by JS)
        self.fields['json_repr'].required = False

    class Meta:
        model = Order
        fields = ['name', 'ordered_at', 'state', 'sales_executive', 'customer', 'json_repr']

        widgets = {
            'name': forms.TextInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Nommer la commande'}),
            'cashed': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Montant encaissé'}),
            'discount': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Montant de la reduction'}),
            'ordered_at': forms.DateInput(attrs={'type': 'date', 'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez la date de la commande'}),
            'sales_executive': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez le nom de l\'apporteur d\'affaire'}),
            'customer': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Choisissez un client'}),
            'state': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Etat de la commande'}),
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
        }


class UpdateOrderForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make json_repr not required in form validation (will be populated by JS)
        self.fields['json_repr'].required = False

    class Meta:
        model = Order
        fields = ['name', 'ordered_at', 'state', 'sales_executive', 'customer', 'json_repr']

        widgets = {
            'name': forms.TextInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Nommer la commande'}),
            'ordered_at': forms.DateInput(attrs={'type': 'date', 'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez la date de la commande'}),
            'discount': forms.NumberInput(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Montant de la reduction'}),
            'ordered_at': forms.DateInput(attrs={'type': 'date', 'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez la date de la commande'}),
            'sales_executive': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Entrez le nom de l\'apporteur d\'affaire'}),
            'customer': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Choisissez un client'}),
            'state': forms.Select(attrs={'class': "border py-1.5 sm:py-2 px-3 pe-11 block w-full border-card-foreground shadow-2xs sm:text-sm rounded-lg focus:border-primary focus:ring-primary checked:border-primary disabled:opacity-50 disabled:pointer-events-none ", 'placeholder': 'Etat de la commande'}),
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
        }