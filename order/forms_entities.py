from django import forms
from order.models import Article, Customer, SalesExecutive


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['name', 'ref', 'sale_price', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Nom de l\'article'
            }),
            'ref': forms.TextInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Référence unique'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Prix de vente',
                'step': '0.01'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4 dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
            }),
        }
        labels = {
            'name': 'Nom',
            'ref': 'Référence',
            'sale_price': 'Prix de vente (FCFA)',
            'photo': 'Photo',
        }


class CustomerForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
            'placeholder': 'Email du client'
        }),
        label='Email'
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
            'placeholder': 'Adresse du client',
            'rows': 3
        }),
        label='Adresse'
    )
    
    class Meta:
        model = Customer
        fields = ['name', 'tel', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Nom du client'
            }),
            'tel': forms.TextInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Téléphone'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4 dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
            }),
        }
        labels = {
            'name': 'Nom',
            'tel': 'Téléphone',
            'photo': 'Photo',
        }


class SalesExecutiveForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
            'placeholder': 'Email de l\'apporteur'
        }),
        label='Email'
    )
    
    class Meta:
        model = SalesExecutive
        fields = ['name', 'tel', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Nom de l\'apporteur'
            }),
            'tel': forms.TextInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Téléphone'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4 dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
            }),
        }
        labels = {
            'name': 'Nom',
            'tel': 'Téléphone',
            'photo': 'Photo',
        }
