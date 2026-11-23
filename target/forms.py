from django import forms
from target.models import Target


class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ['name', 'description', 'article', 'quantity', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Désignation de l\'objectif'
            }),
            'description': forms.Textarea(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Description'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Date de début'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Date de fin'
            }),
            'article': forms.Select(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Choisir un article'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400',
                'placeholder': 'Quantité'
            }),
        }
        labels = {
            'name': 'Nom',
            'description': 'Description',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'article': 'Article',
            'quantity': 'Quantité',
        }
