from django import forms
from .models import ItemEstoque

class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ['nome', 'foto', 'valor', 'quantidade', 'prioridade']