from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.contrib import messages
from user_agents import parse
from .models import Carrinho, ItemCarrinho
from estoque.models import ItemEstoque
import os
from core.utils import is_admin
from core.models import CustomUser
from django.http import JsonResponse
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404

# Função para remover um item do carrinho
@login_required
def remover_item_carrinho(request, item_id):
    carrinho = get_object_or_404(Carrinho, user=request.user, ativo=True)
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)
    item.delete()
    messages.success(request, f"Item {item.item_estoque.nome} removido do carrinho.")
    return redirect('vendas:painel-vendas')

# Função para limpar o carrinho
@login_required
def limpar_carrinho(request):
    carrinho = get_object_or_404(Carrinho, user=request.user, ativo=True)
    carrinho.itens.all().delete()
    messages.success(request, "Carrinho limpo com sucesso.")
    return redirect('vendas:painel-vendas')

# Função para concluir a venda
@login_required
def concluir_venda(request):
    carrinho = Carrinho.objects.get(user=request.user, ativo=True)
    # Forma de pagamento
    if request.method == "POST":
        pagamento = request.POST.get('pagamento', None)
        valor_recebido = request.POST.get('valor_recebido', None)  # Valor recebido em dinheiro
        comprovante_pix = carrinho.comprovante_pix  # Comprovante PIX

        try:
            valor_recebido = Decimal(valor_recebido) if valor_recebido else None
        except:
            valor_recebido = None  # Valor inválido ou não fornecido

        with transaction.atomic():  # Garante que todas as operações sejam atômicas
            # Calcula o valor total da venda
            valor_total = sum(item.total() for item in carrinho.itens.all())
            if carrinho.itens.exists():
                for item_carrinho in carrinho.itens.all():
                    item_estoque = item_carrinho.item_estoque
                    quantidade_vendida = item_carrinho.quantidade

                    # Verifica se o item é 'Folha A4', 'Impressão (1 lado)' ou 'Impressão (2 lados)'
                    if item_estoque.nome in ['Folha A4', 'Impressão (1 lado)', 'Impressão (2 lados)', 'Desperdício']:
                        # Abate a quantidade vendida do estoque dos três itens

                        for nome_item in ['Folha A4', 'Impressão (1 lado)', 'Impressão (2 lados)', 'Desperdício']:
                            item_associado = ItemEstoque.objects.get(nome=nome_item)
                            print(item_associado.nome)
                            if item_associado.quantidade >= quantidade_vendida:
                                item_associado.quantidade -= quantidade_vendida
                                item_associado.save()
                            else:
                                messages.error(request, f"Quantidade insuficiente no estoque para {nome_item}.")
                                return redirect('vendas:painel-vendas')
                    else:
                        # Verifica se há estoque suficiente
                        if item_estoque.quantidade >= quantidade_vendida:
                            item_estoque.quantidade -= quantidade_vendida
                            item_estoque.save()
                        else:
                            messages.error(request, f"Quantidade insuficiente no estoque para {item_estoque.nome}.")
                            return redirect('vendas:painel-vendas')

                # Salva as informações da venda no carrinho
                carrinho.ativo = False
                carrinho.valor_recebido = valor_recebido

                if pagamento != 'pix':
                    carrinho.comprovante_pix = None
                else:
                    carrinho.comprovante_pix = comprovante_pix

                carrinho.data_venda = now()  # Data e hora da venda
                carrinho.valor_total = valor_total
                carrinho.save()

                # Opcional: Você pode criar registros históricos detalhados da venda
                for item_carrinho in carrinho.itens.all():
                    item_carrinho.venda = carrinho  # Associa o item ao carrinho (se necessário)
                    item_carrinho.save()
            else:
                messages.error(request, "O carrinho está vazio!")
                return redirect('vendas:painel-vendas')
            
            messages.success(request, "Venda concluída com sucesso!")

            return redirect('vendas:painel-vendas')  # Ou para onde você quiser redirecionar após a venda ser concluída

    return render(request, 'painel_vendas.html', {'carrinho': carrinho})

# Função para buscar comprovantes
@login_required
def buscar_comprovantes(request, carrinho_id):
    # Calcular a data limite (5 minutos atrás)
    usuario = request.user.username
    
    # Caminho para o diretório onde os comprovantes são armazenados
    comprovantes_dir = "media/comprovantes_pix"

    # Listar arquivos do diretório que correspondem ao timestamp e pegar os comprovantes recentes
    arquivos = [f for f in os.listdir(comprovantes_dir) if f.startswith(usuario)]
    
    if not arquivos:
        return JsonResponse({"comprovantes": []})

    # Ordena os arquivos pelo nome (que contém a data e hora) em ordem decrescente
    arquivos.sort(reverse=True)
    
    # Pega o último arquivo
    ultimo_comprovante = arquivos[0]

    try:
        carrinho = Carrinho.objects.get(id=carrinho_id)
        carrinho.comprovante_pix = ultimo_comprovante  # Atribui o comprovante ao carrinho
        carrinho.save()  # Salva o carrinho atualizado
    except Carrinho.DoesNotExist:
        return JsonResponse({"erro": "Carrinho não encontrado"}, status=404)

    # Retorna o caminho completo do arquivo e outras informações necessárias
    return JsonResponse({"comprovantes": [{"arquivo": ultimo_comprovante}]})

# Função para fazer upload de comprovante
@login_required
def upload_comprovante(request):
    if request.method == 'POST' and request.FILES.get('imagem'):
        imagem = request.FILES['imagem']

        # Encontrar o carrinho ativo do usuário
        carrinho = Carrinho.objects.filter(user=request.user, ativo=True).first()
        
        if carrinho:
            # Gerar o nome do arquivo com o nome do usuário e a data/hora
            timestamp = now().strftime('%Y%m%d_%H%M%S')
            user_name = request.user.username.replace(' ', '_')  # Substituir espaços por underscores, se houver
            ext = imagem.name.split('.')[-1]  # Obtém a extensão do arquivo original
            novo_nome = f"{user_name}_{timestamp}.{ext}"

            # Salvar o arquivo no sistema de arquivos
            fs = FileSystemStorage(location='media/comprovantes_pix/')  # Ajuste o caminho se necessário
            filename = fs.save(novo_nome, imagem)

            # Salvar o caminho no campo 'comprovante_pix' do carrinho
            carrinho.comprovante_pix = f"comprovantes_pix/{novo_nome}"
            carrinho.save()

        return redirect('vendas:painel-mobile')  # Redireciona para a página de finalização de venda ou outra página relevante

    return render(request, 'painel_mobile.html')

# Função para exibir o painel de vendas
@login_required
def painel_vendas(request):
    # Obtém ou cria o carrinho ativo do usuário
    user = request.user

    if user.primeiro_acesso:
        return redirect('usuarios:trocar-senha')
    
    else:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_parsed = parse(user_agent)

        # Verifica se o usuário está acessando pelo celular
        if user_agent_parsed.is_mobile:
            # Redireciona para a nova página para dispositivos móveis
            return redirect('vendas:painel-mobile')

        # Carrega ou cria o carrinho ativo do usuário
        carrinho, created = Carrinho.objects.get_or_create(user=request.user, ativo=True)
        itens_estoque = ItemEstoque.objects.all()

        # Inicializa o total do carrinho
        total = sum(float(item_carrinho.total()) for item_carrinho in carrinho.itens.all())

        # Armazena o timestamp de carregamento da página na sessão
        if 'page_load_time' not in request.session:
            request.session['page_load_time'] = now().isoformat()

        # Exibe comprovantes se PIX for selecionado
        comprovantes = []
        if request.method == "POST" and request.POST.get("pagamento") == "pix":
            page_load_time = request.session.get('page_load_time')
            if page_load_time:
                page_load_time = now().fromisoformat(page_load_time)
                fs = FileSystemStorage(location='media/comprovantes_pix/')
                for filename in fs.listdir('')[1]:  # fs.listdir retorna (diretórios, arquivos)
                    if filename.startswith(request.user.username) and os.path.getmtime(fs.path(filename)) >= page_load_time.timestamp():
                        comprovantes.append(fs.url(filename))

        # Processa a adição de itens ao carrinho
        if request.method == "POST" and request.POST.get("item"):
            item_nome = request.POST.get("item")
            quantidade = int(request.POST.get("quantidade", 0))
            
            # Valida o item no estoque
            try:
                item = ItemEstoque.objects.get(nome=item_nome)
            except ItemEstoque.DoesNotExist:
                messages.error(request, "O item não foi encontrado no estoque.")
                return redirect('vendas:painel-vendas')

            # Verifica estoque
            if item.quantidade < quantidade:
                messages.error(request, "Quantidade insuficiente no estoque.")
                return redirect('vendas:painel-vendas')

            # Adiciona ao carrinho
            item_carrinho, created = ItemCarrinho.objects.get_or_create(
                carrinho=carrinho,
                item_estoque=item,
                defaults={'quantidade': quantidade, 'preco_unitario': item.valor}
            )
            if not created:
                item_carrinho.quantidade += quantidade
                item_carrinho.save()

            messages.success(request, f"{item.nome} foi adicionado ao carrinho.")
            return redirect('vendas:painel-vendas')

        return render(request, 'painel_vendas.html', {
            'itens_estoque': itens_estoque,
            'carrinho': carrinho,
            'total': total,
            'comprovantes': comprovantes,
        })

# Função para exibir o painel de vendas para administradores
@user_passes_test(is_admin)
def vendas_admin(request):
    if 'limpar_filtros' in request.GET:
        return redirect('vendas:vendas-admin')

    # Filtros básicos
    data_inicial = request.GET.get('data_inicial', None)
    data_final = request.GET.get('data_final', None)
    usuario = request.GET.get('usuario', None)

    # Aplicando filtro por data
    vendas = Carrinho.objects.all()

    if usuario:
        vendas = vendas.filter(user=usuario)

    if data_inicial:
        vendas = vendas.filter(data_venda__gte=data_inicial)

    if data_final:
        vendas = vendas.filter(data_venda__lte=data_final)

    vendas = vendas.order_by('-data_venda')

    # Paginação
    paginator = Paginator(vendas, 10)  # Mostra 10 vendas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    usuarios = CustomUser.objects.all()

    return TemplateResponse(request, 'vendas_admin.html', {
        'page_obj': page_obj,
        'usuarios': usuarios,
    })