from django.shortcuts import render
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from core.utils import is_admin
from .models import HorarioFuncionamento, ExcecaoHorario
from .forms import HorarioFuncionamentoForm, ExcecaoHorarioForm

# Decorador que verifica se o usuário é administrador antes de acessar a view
@user_passes_test(is_admin)
def editar_horario(request, pk):
    # Obtém o objeto HorarioFuncionamento pelo pk ou retorna 404 se não encontrado
    horario = get_object_or_404(HorarioFuncionamento, pk=pk)
    if request.method == 'POST':
        # Cria um formulário com os dados enviados no POST e a instância do horário
        form = HorarioFuncionamentoForm(request.POST, instance=horario)
        if form.is_valid():
            # Se o formulário for válido, salva as alterações e retorna um JsonResponse de sucesso
            form.save()
            return JsonResponse({'success': True})
        else:
            # Se o formulário não for válido, retorna um JsonResponse com os erros
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # Se o método não for POST, cria um formulário com a instância do horário
        form = HorarioFuncionamentoForm(instance=horario)
        return render(request, 'editar_horario_form.html', {'form': form, 'horario': horario})

# Decorador que verifica se o usuário é administrador antes de acessar a view
@user_passes_test(is_admin)
def excluir_horario(request, pk):
    # Obtém o objeto HorarioFuncionamento pelo pk ou retorna 404 se não encontrado
    horario = get_object_or_404(HorarioFuncionamento, pk=pk)
    if request.method == 'POST':
        # Se o método for POST, deleta o horário e retorna um JsonResponse de sucesso
        horario.delete()
        return JsonResponse({'success': True})
    # Se o método não for POST, retorna um JsonResponse de falha
    return JsonResponse({'success': False})

# Decorador que verifica se o usuário é administrador antes de acessar a view
@user_passes_test(is_admin)
def editar_excecao(request, pk):
    # Obtém o objeto ExcecaoHorario pelo pk ou retorna 404 se não encontrado
    excecao = get_object_or_404(ExcecaoHorario, pk=pk)
    if request.method == 'POST':
        # Cria um formulário com os dados enviados no POST e a instância da exceção
        form = ExcecaoHorarioForm(request.POST, instance=excecao)
        if form.is_valid():
            # Se o formulário for válido, salva as alterações e retorna um JsonResponse de sucesso
            form.save()
            return JsonResponse({'success': True})
        else:
            # Se o formulário não for válido, retorna um JsonResponse com os erros
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # Se o método não for POST, cria um formulário com a instância da exceção
        form = ExcecaoHorarioForm(instance=excecao)
        return render(request, 'editar_excecao_form.html', {'form': form, 'excecao': excecao})

# Decorador que verifica se o usuário é administrador antes de acessar a view
@user_passes_test(is_admin)
def excluir_excecao(request, pk):
    # Obtém o objeto ExcecaoHorario pelo pk ou retorna 404 se não encontrado
    excecao = get_object_or_404(ExcecaoHorario, pk=pk)
    if request.method == 'POST':
        # Se o método for POST, deleta a exceção e retorna um JsonResponse de sucesso
        excecao.delete()
        return JsonResponse({'success': True})
    # Se o método não for POST, retorna um JsonResponse de falha
    return JsonResponse({'success': False})

# Decorador que verifica se o usuário é administrador antes de acessar a view
@user_passes_test(is_admin)
def gerenciar_horarios(request):
    # Obtém todos os objetos HorarioFuncionamento ordenados por dia da semana e abertura
    horarios = HorarioFuncionamento.objects.all().order_by('dia_semana', 'abertura')
    # Obtém todas as exceções de horário ordenadas por data e abertura
    excecoes = ExcecaoHorario.objects.all().order_by('data', 'horario__abertura')

    if request.method == 'POST':
        if 'adicionar_horario' in request.POST:
            # Cria um formulário com os dados enviados no POST para adicionar um novo horário
            horario_form = HorarioFuncionamentoForm(request.POST)
            if horario_form.is_valid():
                # Se o formulário for válido, salva o novo horário e redireciona para a página de gerenciamento
                horario_form.save()
                return redirect('horarios:gerenciar-horarios')

        elif 'adicionar_excecao' in request.POST:
            # Cria um formulário com os dados enviados no POST para adicionar uma nova exceção
            excecao_form = ExcecaoHorarioForm(request.POST)
            if excecao_form.is_valid():
                # Se o formulário for válido, salva a nova exceção e redireciona para a página de gerenciamento
                excecao_form.save()
                return redirect('horarios:gerenciar-horarios')

    else:
        # Se o método não for POST, cria formulários vazios para adicionar novos horários e exceções
        horario_form = HorarioFuncionamentoForm()
        excecao_form = ExcecaoHorarioForm()

    # Renderiza a página de gerenciamento de horários com os horários, exceções e formulários
    return TemplateResponse(request, "gerenciar_horarios.html", {
        "horarios": horarios,
        "excecoes": excecoes,
        "horario_form": horario_form,
        "excecao_form": excecao_form,
    })
