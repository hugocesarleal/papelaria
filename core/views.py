from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import user_passes_test
from .models import ItemEstoque
from .forms import ItemEstoqueForm
from django.conf import settings
import os
from .models import Cliente 
from django.http import HttpResponseRedirect
from .forms import ClienteForm
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from .models import ItemEstoque, Carrinho, ItemCarrinho
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
from user_agents import parse
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from django.utils.timezone import now
from .models import Carrinho
from django.utils.dateparse import parse_datetime
from django.utils import timezone

def buscar_comprovantes(request):
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

    # Retorna o caminho completo do arquivo e outras informações necessárias
    return JsonResponse({"comprovantes": [{"arquivo": ultimo_comprovante}]})

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

        return redirect('nova-pagina')  # Redireciona para a página de finalização de venda ou outra página relevante

    return render(request, 'core/painel_mobile.html')

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

@login_required
def concluir_venda(request):
    carrinho = Carrinho.objects.get(user=request.user, ativo=True)

    if request.method == "POST":
        # Aqui você pode processar a venda
        with transaction.atomic():  # Garante que todas as operações sejam atômicas
            for item_carrinho in carrinho.itens.all():
                item_estoque = item_carrinho.item_estoque
                quantidade_vendida = item_carrinho.quantidade

                # Verifica se há estoque suficiente
                if item_estoque.quantidade >= quantidade_vendida:
                    item_estoque.quantidade -= quantidade_vendida
                    item_estoque.save()
                else:
                    # Se não houver estoque suficiente, pode lançar um erro ou informar ao usuário
                    return render(request, 'core/erro_estoque.html', {
                        'item': item_estoque,
                        'quantidade': quantidade_vendida
                    })

            # Após concluir a venda, você pode marcar o carrinho como inativo
            carrinho.ativo = False
            carrinho.save()

            return redirect('painel-vendas')  # Ou para onde você quiser redirecionar após a venda ser concluída

    return render(request, 'core/painel_vendas.html', {'carrinho': carrinho})

@login_required
def painel_vendas(request):
    # Obtém ou cria o carrinho ativo do usuário
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    user_agent_parsed = parse(user_agent)

    # Verifica se o usuário está acessando pelo celular
    if user_agent_parsed.is_mobile:
        # Redireciona para a nova página para dispositivos móveis
        return redirect('nova-pagina')

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
            return redirect('painel-vendas')

        # Verifica estoque
        if item.quantidade < quantidade:
            messages.error(request, "Quantidade insuficiente no estoque.")
            return redirect('painel-vendas')

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
        return redirect('painel-vendas')

    return render(request, 'core/painel_vendas.html', {
        'itens_estoque': itens_estoque,
        'carrinho': carrinho,
        'total': total,
        'comprovantes': comprovantes,
    })

def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar-estoque')  # Volta para a página de estoque
    else:
        form = ClienteForm()
    return render(request, 'core/estoque/listar_estoque.html', {'form': form})

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def user_list(request):
    users = get_user_model().objects.all()
    return render(request, 'core/user_list.html', {'users': users})
    
@user_passes_test(is_admin)
def create_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('admin-dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'core/create_user.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('admin-dashboard')
            else:
                return redirect('painel-vendas')
        else:
            return render(request, 'core/login.html', {'error': 'Credenciais inválidas'})
    return render(request, 'core/login.html')


@user_passes_test(is_admin)
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('user-dashboard')

    clientes = Cliente.objects.all()

    if request.method == "POST":
        assunto = request.POST.get("assunto")
        mensagem = request.POST.get("mensagem")
        destinatarios = [cliente.email for cliente in clientes]

        if assunto and mensagem:
            send_mail(
                assunto,
                mensagem,
                'seu_email@dominio.com',  # Substitua pelo e-mail do remetente
                destinatarios,
                fail_silently=False,
            )
            return redirect('admin-dashboard')

    return render(request, 'core/admin_dashboard.html', {'clientes': clientes})

@user_passes_test(is_admin)
def admin_dashboard_clientes(request):
    if not request.user.is_staff:
        return redirect('user-dashboard')

    clientes = Cliente.objects.all()

    if request.method == "POST":
        assunto = request.POST.get("assunto")
        mensagem = request.POST.get("mensagem")
        destinatarios = [cliente.email for cliente in clientes]
        arquivos = request.FILES.getlist('arquivos')  # Obtém os arquivos enviados

        if assunto and mensagem:
            # Criando a mensagem de e-mail
            email = EmailMessage(
                subject=assunto,
                body=mensagem,
                from_email='seu_email@dominio.com',  # Substitua pelo e-mail do remetente
            )
            # Usando BCC para enviar para múltiplos destinatários sem mostrar seus e-mails
            email.bcc = destinatarios
            
            # Anexando arquivos, se houver
            for arquivo in arquivos:
                email.attach(arquivo.name, arquivo.read(), arquivo.content_type)

            # Enviando o e-mail
            email.send(fail_silently=False)

            # Redireciona após o envio
            return redirect('admin-dashboard-clientes')

    return render(request, 'core/admin_dashboard_clientes.html', {'clientes': clientes})

@login_required
def user_dashboard(request):
    return render(request, 'core/user_dashboard.html')

@user_passes_test(is_admin)
def listar_estoque_admin(request):
    if not request.user.is_staff:
        return redirect('user-dashboard')
    itens = ItemEstoque.objects.all()
    return render(request, 'core/estoque/listar_estoque_admin.html', {'itens': itens})

@user_passes_test(is_admin)
def adicionar_item(request):
    if not request.user.is_staff:
        return redirect('user-dashboard')
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar-estoque-admin')
    else:
        form = ItemEstoqueForm()
    return render(request, 'core/estoque/adicionar_item.html', {'form': form})

@user_passes_test(is_admin)
def editar_item(request, pk):
    if not request.user.is_staff:
        return redirect('user-dashboard')
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('listar-estoque-admin')
    else:
        form = ItemEstoqueForm(instance=item)
    return render(request, 'core/estoque/editar_item.html', {'form': form, 'item': item})

@login_required
def remover_item(request, pk):
    if not request.user.is_staff:
        return redirect('user-dashboard')
    
    item = get_object_or_404(ItemEstoque, pk=pk)
    
    if request.method == 'POST':
        if item.foto:
            try:
                if os.path.isfile(item.foto.path):
                    os.remove(item.foto.path)
            except Exception as e:
                print(f"Erro ao remover imagem: {e}")
        item.delete()
        return redirect('listar-estoque-admin')

    return render(request, 'core/estoque/remover_item.html', {'item': item})

def listar_estoque(request):
    itens = ItemEstoque.objects.all()
    return render(request, 'core/estoque/listar_estoque.html', {'itens': itens})

@login_required
def remover_item_carrinho(request, item_id):
    carrinho = get_object_or_404(Carrinho, user=request.user, ativo=True)
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)
    item.delete()
    messages.success(request, f"Item {item.item_estoque.nome} removido do carrinho.")
    return redirect('painel-vendas')

@login_required
def limpar_carrinho(request):
    carrinho = get_object_or_404(Carrinho, user=request.user, ativo=True)
    carrinho.itens.all().delete()
    messages.success(request, "Carrinho limpo com sucesso.")
    return redirect('painel-vendas')