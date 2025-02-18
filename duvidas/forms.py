from django import forms
from .models import Duvida

class ResponderDuvidaForm(forms.ModelForm):
    class Meta:
        model = Duvida
        fields = ['resposta']
