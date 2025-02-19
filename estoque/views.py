from django.shortcuts import render
from django.http import JsonResponse
from .models import ItemEstoque
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ItemEstoqueForm
from django.contrib.auth.decorators import user_passes_test
import os
from core.utils import is_admin
from django.template.response import TemplateResponse
from django.db.models import Case, When, IntegerField

# Função para buscar itens no estoque com base em uma query
def buscar_itens(request):
    query = request.GET.get('q', '')
    itens = ItemEstoque.objects.filter(nome__icontains=query)[:10]  # Retorna no máximo 10 itens

    resultados = []
    for item in itens:
        resultados.append({
            'id': item.id,
            'nome': item.nome,
            'foto': item.foto.url,  # URL da imagem do item
            'quantidade': item.quantidade,
        })

    return JsonResponse(resultados, safe=False)

# Função para listar itens do estoque para administradores
@user_passes_test(is_admin)
def listar_estoque_admin(request):
    itens = ItemEstoque.objects.annotate(
        esgotado=Case(
            When(quantidade=0, then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('esgotado', '-prioridade', 'nome')
    
    return TemplateResponse(request, 'listar_estoque_admin.html', {'itens': itens})

# Função para adicionar um novo item ao estoque
@user_passes_test(is_admin)
def adicionar_item(request):
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('estoque:listar-estoque-admin')
    else:
        form = ItemEstoqueForm()
    return render(request, 'adicionar_item.html', {'form': form})

# Função para editar um item existente no estoque
@user_passes_test(is_admin)
def editar_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('estoque:listar-estoque-admin')
    else:
        form = ItemEstoqueForm(instance=item)
    return render(request, 'editar_item.html', {'form': form, 'item': item})

# Função para remover um item do estoque
@user_passes_test(is_admin)
def remover_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    
    if request.method == 'POST':
        if item.foto:
            try:
                if os.path.isfile(item.foto.path):
                    os.remove(item.foto.path)
            except Exception as e:
                print(f"Erro ao remover imagem: {e}")
        item.delete()
        return redirect('estoque:listar-estoque-admin')

    return render(request, 'remover_item.html', {'item': item})
