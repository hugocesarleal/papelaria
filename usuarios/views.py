from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.template.response import TemplateResponse
from django.contrib.auth import get_user_model
from .forms import NovoPasswordForm
from django.contrib.auth import update_session_auth_hash
from core.utils import is_admin

@login_required
def trocar_senha(request):
    user = request.user
    if user.primeiro_acesso:  # Verifica se é o primeiro acesso
        if request.method == 'POST':
            form = NovoPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()  # Salva a nova senha
                user.primeiro_acesso = False  # Marca como false após a troca de senha
                user.save()  # Salva o usuário com a nova informação
                update_session_auth_hash(request, user)  # Atualiza a sessão
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('core:home')  # Redireciona para a página de sua escolha
            else:
                messages.error(request, 'Por favor, corrija os erros abaixo.')
        else:
            form = NovoPasswordForm(user)

        return TemplateResponse(request, 'trocar_senha.html', {'form': form})

    else:
        return redirect('core:home')  # Se não for primeiro acesso, redireciona para outra página

@user_passes_test(is_admin)
def editar_usuario(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('usuarios:usuarios')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'editar_usuario_form.html', {'form': form, 'user': user})

@user_passes_test(is_admin)
def usuarios(request):
    
    if request.user.primeiro_acesso:
        return redirect('usuarios:trocar-senha')
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('usuarios:usuarios')
    else:
        form = CustomUserCreationForm()

    users = get_user_model().objects.all()

    return TemplateResponse(request, 'usuarios.html', {'form': form, 'users': users})

@user_passes_test(is_admin)
def excluir_usuario(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('usuarios:usuarios')
    
    return render(request, 'excluir_usuario.html', {'user': user})
