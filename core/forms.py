from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import ItemEstoque
from .models import Cliente, Aviso
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

class NovoPasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

class AvisoForm(forms.ModelForm):
    class Meta:
        model = Aviso
        fields = ['texto', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

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
    primeiro_acesso = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'is_admin', 'primeiro_acesso')
