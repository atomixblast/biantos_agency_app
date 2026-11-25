from django import forms

from target.models import Target


INPUT_CLASS = (
    'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm '
    'focus:border-primary focus:ring-primary dark:bg-neutral-900 '
    'dark:border-neutral-700 dark:text-neutral-400'
)


class TargetForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sales_executive'].empty_label = "Toute l'agence"
        self.fields['article'].empty_label = 'Choisir un article'
        self.fields['article'].required = False  # obligatoire selon le type, vérifié dans Target.clean()
        for name, f in self.fields.items():
            if name != 'metric':
                f.widget.attrs.setdefault('class', INPUT_CLASS)

    class Meta:
        model = Target
        fields = ['name', 'metric', 'target_value', 'article', 'sales_executive',
                  'start_date', 'end_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Ex. : Ventes de décembre"}),
            'metric': forms.RadioSelect(attrs={'x-model': 'metric', 'class': 'text-primary focus:ring-primary'}),
            'target_value': forms.NumberInput(attrs={'placeholder': 'Valeur à atteindre', 'min': '0', 'step': 'any'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Description (optionnel)'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'x-ref': 'start'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'type': 'date', 'x-ref': 'end'}, format='%Y-%m-%d'),
        }
        labels = {
            'name': 'Nom',
            'metric': "Type d'objectif",
            'target_value': 'Objectif à atteindre',
            'article': 'Article',
            'sales_executive': 'Attribué à',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'description': 'Description',
        }
