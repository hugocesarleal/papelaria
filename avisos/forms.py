from django import forms
from .models import Aviso

class AvisoForm(forms.ModelForm):
    class Meta:
        model = Aviso
        fields = ['texto', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }