from django import forms
from .models import DocumentoImpressao

class DocumentoImpressaoForm(forms.ModelForm):
    class Meta:
        model = DocumentoImpressao
        fields = ['nome_cliente']
        labels = {
            'nome_cliente': 'Nome do Cliente',
        }