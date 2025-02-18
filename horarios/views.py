from django.shortcuts import render
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from core.utils import is_admin
from .models import HorarioFuncionamento, ExcecaoHorario
from .forms import HorarioFuncionamentoForm, ExcecaoHorarioForm

@user_passes_test(is_admin)
def editar_horario(request, pk):
    horario = get_object_or_404(HorarioFuncionamento, pk=pk)
    if request.method == 'POST':
        form = HorarioFuncionamentoForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = HorarioFuncionamentoForm(instance=horario)
        return render(request, 'editar_horario_form.html', {'form': form, 'horario': horario})

@user_passes_test(is_admin)
def excluir_horario(request, pk):
    horario = get_object_or_404(HorarioFuncionamento, pk=pk)
    if request.method == 'POST':
        horario.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@user_passes_test(is_admin)
def editar_excecao(request, pk):
    excecao = get_object_or_404(ExcecaoHorario, pk=pk)
    if request.method == 'POST':
        form = ExcecaoHorarioForm(request.POST, instance=excecao)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ExcecaoHorarioForm(instance=excecao)
        return render(request, 'editar_excecao_form.html', {'form': form, 'excecao': excecao})

@user_passes_test(is_admin)
def excluir_excecao(request, pk):
    excecao = get_object_or_404(ExcecaoHorario, pk=pk)
    if request.method == 'POST':
        excecao.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@user_passes_test(is_admin)
def gerenciar_horarios(request):
    # Ordena os horários pela ordem do dia da semana e horário de abertura
    horarios = HorarioFuncionamento.objects.all().order_by('dia_semana', 'abertura')

    # Ordena as exceções pela data e horário de abertura
    excecoes = ExcecaoHorario.objects.all().order_by('data', 'horario__abertura')

    if request.method == 'POST':
        if 'adicionar_horario' in request.POST:
            horario_form = HorarioFuncionamentoForm(request.POST)
            if horario_form.is_valid():
                horario_form.save()
                return redirect('horarios:gerenciar-horarios')

        elif 'adicionar_excecao' in request.POST:
            excecao_form = ExcecaoHorarioForm(request.POST)
            if excecao_form.is_valid():
                excecao_form.save()
                return redirect('horarios:gerenciar-horarios')

    else:
        horario_form = HorarioFuncionamentoForm()
        excecao_form = ExcecaoHorarioForm()

    return TemplateResponse(request, "gerenciar_horarios.html", {
        "horarios": horarios,
        "excecoes": excecoes,
        "horario_form": horario_form,
        "excecao_form": excecao_form,
    })
