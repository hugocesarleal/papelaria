from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from core.models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

class NovoPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nova senha'}),
    )
    new_password2 = forms.CharField(
        label="Confirme a nova senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme a nova senha'}),
    )

    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'is_staff', 'primeiro_acesso')

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_admin = forms.BooleanField(required=False, initial=False)
    primeiro_acesso = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'is_admin', 'primeiro_acesso')