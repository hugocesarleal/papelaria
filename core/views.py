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

def buscar_itens(request):
    query = request.GET.get('q', '')
    itens = ItemEstoque.objects.filter(nome__icontains=query)[:10]  # Retorna no máximo 10 itens

    resultados = []
    for item in itens:
        resultados.append({
            'id': item.id,
            'nome': item.nome,
            'foto': item.foto.url,  # URL da imagem do item
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
    carrinho, created = Carrinho.objects.get_or_create(user=request.user, ativo=True)
    itens_estoque = ItemEstoque.objects.all()

    total = 0  # Inicializa o total do carrinho
    for item_carrinho in carrinho.itens.all():
        total += item_carrinho.total()  # Adiciona o total de cada item ao total geral

    if request.method == "POST":
        item_nome = request.POST.get("item")  # O nome do item será passado
        quantidade = int(request.POST.get("quantidade"))
        pagamento = request.POST.get("pagamento")
        
        # Tentativa de encontrar o item pelo nome
        try:
            item = ItemEstoque.objects.get(nome=item_nome)
        except ItemEstoque.DoesNotExist:
            messages.error(request, "O item não foi encontrado no estoque.")
            return redirect('painel-vendas')

        # Verifica se a quantidade disponível é suficiente
        if item.quantidade < quantidade:
            messages.error(request, "Quantidade insuficiente no estoque.")
            return redirect('painel-vendas')

        # Adiciona o item ao carrinho
        item_carrinho, created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho,
            item_estoque=item,
            defaults={'quantidade': quantidade, 'preco_unitario': item.valor}
        )

        if not created:  # Caso o item já esteja no carrinho, atualiza a quantidade
            item_carrinho.quantidade += quantidade
            item_carrinho.save()

        item.save()

        messages.success(request, f"{item.nome} foi adicionado ao carrinho.")
        return redirect('painel-vendas')

    return render(request, 'core/painel_vendas.html', {'itens_estoque': itens_estoque, 'carrinho': carrinho, 'total': total})

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