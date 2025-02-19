from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from .models import Aviso
from .forms import AvisoForm
from core.utils import is_admin

# Função para listar avisos, acessível apenas para administradores
@user_passes_test(is_admin)
def listar_avisos(request):
    agora = timezone.now()
    avisos = Aviso.objects.filter(data_fim__gte=agora)  # Filtra avisos cuja data de término é maior ou igual ao momento atual
    if request.method == 'POST':
        form = AvisoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aviso criado/atualizado com sucesso!')
            return redirect('avisos:listar-avisos')
    else:
        form = AvisoForm()
    return TemplateResponse(request, 'listar_avisos.html', {'avisos': avisos, 'form': form})

# Função para editar um aviso específico, acessível apenas para administradores
@user_passes_test(is_admin)
def editar_aviso(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    if request.method == 'POST':
        form = AvisoForm(request.POST, instance=aviso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aviso atualizado com sucesso!')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = AvisoForm(instance=aviso)
        return render(request, 'editar_aviso_form.html', {'form': form, 'aviso': aviso})

# Função para excluir um aviso específico, acessível apenas para administradores
@user_passes_test(is_admin)
def excluir_aviso(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    if request.method == 'POST':
        aviso.delete()
        messages.success(request, 'Aviso excluído com sucesso!')
        return redirect('avisos:listar-avisos')
    return redirect('avisos:listar-avisos')
