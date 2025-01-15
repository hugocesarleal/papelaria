from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import ItemEstoque
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone']


class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ['nome', 'descricao', 'foto', 'valor', 'quantidade']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_admin = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'is_admin')
