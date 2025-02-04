from .models import ItemEstoque, Cliente, CustomUser, Carrinho, ItemCarrinho, RegistroPonto, Configuracao, CustomUser, Aviso, Visita
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ItemEstoqueForm, ClienteForm, CustomUserCreationForm, AvisoForm
from django.contrib.auth import get_user_model, logout as auth_logout
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth import authenticate, login
from django.utils.dateparse import parse_datetime
from datetime import datetime, date, timedelta
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.db.models import F
from django.db.models import Q
from user_agents import parse
from decimal import Decimal
from django.db.models import Case, When
from django.core.paginator import Paginator
import os
from django.conf.urls.static import static
from django.contrib.auth import update_session_auth_hash
from .forms import NovoPasswordForm
from django.utils.timezone import localtime, now
from .models import HorarioFuncionamento, ExcecaoHorario
from .forms import HorarioFuncionamentoForm, ExcecaoHorarioForm
from .models import HorarioFuncionamento, ExcecaoHorario
from .forms import HorarioFuncionamentoForm, ExcecaoHorarioForm
from django.template.response import TemplateResponse
from .forms import CustomUserChangeForm
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Duvida
from .forms import ResponderDuvidaForm
import difflib
from django.core.mail import BadHeaderError, send_mail
import re
from django.db.models import Case, When, IntegerField
from django.db import models

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').lower()

        # Respostas padronizadas
        respostas = {
            'horário de funcionamento': 'Consulte nossos horários de funcionamento clicando no ícone no menu lateral.',
            'horário': 'Consulte nossos horários de funcionamento clicando no ícone no menu lateral.',
            'abre': 'Consulte nossos horários de funcionamento clicando no ícone no menu lateral.',
            'abrir': 'Consulte nossos horários de funcionamento clicando no ícone no menu lateral.',
            'aberto': 'Para saber se a papelaria está aberta, basta conferir o aviso no canto superior direito da página.',
            'endereço': 'Estamos localizados no prédio do DCE, ao lado da biblioteca.',
            'localização': 'Estamos localizados no prédio do DCE, ao lado da biblioteca.',
            'valores': 'Os valores dos itens vendidos podem ser consultados na página inicial.',
            'preços': 'Os valores dos itens vendidos podem ser consultados na página inicial.',
            'contato': 'Você pode nos contatar pelo email dce.guytorres@gmail.com.',
            'formas de pagamento': 'Aceitamos pagamentos em dinheiro e PIX.',
            'dinheiro': 'Aceitamos pagamentos em dinheiro e PIX.',
            'pix': 'Aceitamos pagamentos em dinheiro e PIX.',
            'promoções': 'Cadastre seu email no site para saber sobre promoções e descontos.',
            'ajuda': 'Se precisar de ajuda, entre em contato conosco pelo email dce.guytorres@gmail.com.'
        }

        # Verifica se a mensagem contém alguma palavra-chave ou similar
        for chave, resposta in respostas.items():
            if re.search(r'\b' + re.escape(chave) + r'\b', message):
                return JsonResponse({'response': resposta})

        # Filtragem com difflib para encontrar a resposta mais próxima
        palavras_chave = list(respostas.keys())
        melhor_correspondencia = difflib.get_close_matches(message, palavras_chave, n=1, cutoff=0.6)
        if melhor_correspondencia:
            return JsonResponse({'response': respostas[melhor_correspondencia[0]]})

        return JsonResponse({'response': None})
    return JsonResponse({'response': 'Método não permitido.'}, status=405)

@csrf_exempt
def save_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')

            # Verifica se os dados foram recebidos corretamente
            if not name or not email or not message:
                return JsonResponse({'success': False, 'error': 'Dados incompletos'}, status=400)

            # Salva a dúvida no banco de dados
            duvida = Duvida(nome=name, email=email, mensagem=message)
            duvida.save()

            # Enviar notificação para o administrador
            subject = 'Nova dúvida registrada'
            notification_message = f"""
            Uma nova dúvida foi registrada no sistema.

            Nome: {name}
            Email: {email}
            Mensagem: {message}

            Acesse o painel de administração para responder a dúvida.
            """
            send_mail(
                subject,
                notification_message,
                'dce.guytorres@gmail.com',
                ['hugocesarleal@gmail.com'],
                fail_silently=False,
            )

            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Erro ao decodificar JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

def teste(request):
    return render(request, 'core/teste.html')

def custom_logout(request):
    request.session.flush()
    auth_logout(request)  # Isso faz o logout do usuário
    return redirect('login')

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def responder_duvidas(request):
    duvidas = Duvida.objects.filter(respondida=False)
    if request.method == 'POST':
        form = ResponderDuvidaForm(request.POST)
        if form.is_valid():
            duvida_id = request.POST.get('duvida_id')
            duvida = get_object_or_404(Duvida, id=duvida_id)
            duvida.resposta = form.cleaned_data['resposta']
            duvida.respondida = True
            duvida.save()
            # Enviar email para o cliente
            subject = 'Resposta à sua dúvida'
            message = f"""
            Olá {duvida.nome},

            Você nos enviou a seguinte dúvida:
            {duvida.mensagem}

            Nossa resposta:
            {duvida.resposta}

            Se você tiver mais alguma dúvida, não hesite em nos contatar.

            Atenciosamente,
            Equipe Papelaria
            """
            try:
                send_mail(
                    subject,
                    message,
                    'admin@papelaria.com',
                    [duvida.email],
                    fail_silently=False,
                )
            except BadHeaderError:
                messages.error(request, 'Erro ao enviar o email. A dúvida foi marcada como respondida, mas o email não pôde ser enviado.')
                return redirect('responder_duvidas')
            except Exception as e:
                messages.error(request, f'Erro ao enviar o email. A dúvida foi marcada como respondida, mas o email não pôde ser enviado.')
                return redirect('responder_duvidas')

            messages.success(request, 'Dúvida respondida e email enviado com sucesso.')
            return redirect('responder_duvidas')
    else:
        form = ResponderDuvidaForm()
    return TemplateResponse(request, 'core/responder_duvidas.html', {'duvidas': duvidas, 'form': form})

@user_passes_test(is_admin)
def editar_usuario(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('usuarios')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'core/editar_usuario_form.html', {'form': form, 'user': user})

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
        return render(request, 'core/editar_horario_form.html', {'form': form, 'horario': horario})

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
        return render(request, 'core/editar_excecao_form.html', {'form': form, 'excecao': excecao})

@user_passes_test(is_admin)
def excluir_excecao(request, pk):
    excecao = get_object_or_404(ExcecaoHorario, pk=pk)
    if request.method == 'POST':
        excecao.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def papelaria_aberta():
    # Pega o horário atual
    hora_atual = timezone.localtime(timezone.now()).time()
    dia_semana_atual = timezone.localtime(timezone.now()).weekday()

    # Obtém os horários cadastrados
    horarios = HorarioFuncionamento.objects.filter(dia_semana=dia_semana_atual)

    # Verifica se há exceções para o horário de hoje
    excecoes = ExcecaoHorario.objects.filter(data=timezone.localtime(timezone.now()).date())

    for horario in horarios:
        # Se a hora atual está dentro do horário de funcionamento
        if horario.abertura <= hora_atual <= horario.fechamento:
            # Verifica se há exceções para esse horário
            for excecao in excecoes:
                if excecao.horario == horario:  # Comparando com o horário específico
                    return False  # A papelaria está fechada por causa da exceção

            # Se não houve exceção, a papelaria está aberta
            return True

    # Se não encontrou nenhum horário válido, a papelaria está fechada
    return False

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
                return redirect('gerenciar-horarios')

        elif 'adicionar_excecao' in request.POST:
            excecao_form = ExcecaoHorarioForm(request.POST)
            if excecao_form.is_valid():
                excecao_form.save()
                return redirect('gerenciar-horarios')

    else:
        horario_form = HorarioFuncionamentoForm()
        excecao_form = ExcecaoHorarioForm()

    return TemplateResponse(request, "core/gerenciar_horarios.html", {
        "horarios": horarios,
        "excecoes": excecoes,
        "horario_form": horario_form,
        "excecao_form": excecao_form,
    })

@user_passes_test(is_admin)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('admin-dashboard-clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'core/editar_cliente.html', {'form': form, 'cliente': cliente})

@user_passes_test(is_admin)
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('admin-dashboard-clientes')
    
    return render(request, 'core/excluir_cliente.html', {'cliente': cliente})

@user_passes_test(is_admin)
def listar_avisos(request):
    agora = timezone.now()
    avisos = Aviso.objects.filter(data_fim__gte=agora)
    if request.method == 'POST':
        form = AvisoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aviso criado/atualizado com sucesso!')
            return redirect('listar-avisos')
    else:
        form = AvisoForm()
    return TemplateResponse(request, 'core/listar_avisos.html', {'avisos': avisos, 'form': form})

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
        return render(request, 'core/editar_aviso_form.html', {'form': form, 'aviso': aviso})

@user_passes_test(is_admin)
def excluir_aviso(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    if request.method == 'POST':
        aviso.delete()
        messages.success(request, 'Aviso excluído com sucesso!')
        return redirect('listar-avisos')
    return redirect('listar-avisos')

@user_passes_test(is_admin)
def vendas_admin(request):

    if 'limpar_filtros' in request.GET:
        return redirect('vendas-admin')
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

    usuarios = CustomUser.objects.all()

    return TemplateResponse(request, 'core/vendas_admin.html', {
        'vendas': vendas,
        'usuarios': usuarios,
    })

@user_passes_test(is_admin)
def consulta_pontos(request):
    # Verifica se o formulário foi enviado para atualizar o valor da hora
    if request.method == 'POST' and 'atualizar_valor_hora' in request.POST:
        novo_valor_hora = request.POST.get('valor_hora')
        # Corrige o formato do valor da hora (substituindo vírgula por ponto)
        novo_valor_hora = novo_valor_hora.replace('.', '').replace('R$ ', '').replace(',', '.')
        
        try:
            config = Configuracao.objects.get(id=1)
            config.valor_hora = novo_valor_hora
            config.save()
        except Configuracao.DoesNotExist:
            Configuracao.objects.create(id=1, valor_hora=novo_valor_hora)

        messages.success(request, 'Valor da hora atualizado com sucesso!')

    # Se o botão de "Limpar Filtros" for pressionado, limpa os filtros
    if 'limpar_filtros' in request.GET:
        return redirect('consulta_pontos')  # Redireciona para a página de consulta sem filtros aplicados

    # Obtém parâmetros de filtro do request
    usuario_id = request.GET.get('usuario', None)
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)

    # Obtém o valor da hora registrado
    valor_hora = Configuracao.get_valor_hora()

    # Converte valor_hora para float, caso seja decimal
    try:
        valor_hora = float(valor_hora)
    except ValueError:
        valor_hora = 0.0  # Caso o valor seja inválido

    # Filtro de registros de ponto
    registros = RegistroPonto.objects.all()

    if usuario_id:
        registros = registros.filter(usuario_id=usuario_id)

    if data_inicio:
        registros = registros.filter(data__gte=data_inicio)

    if data_fim:
        registros = registros.filter(data__lte=data_fim)

    # Ordena os registros do mais recente para o mais antigo, considerando data e hora
    registros = registros.order_by('-data', '-entrada')

    # Calculando o total a pagar para o usuário selecionado
    total_a_pagar = 0
    for registro in registros:
        if registro.total_trabalhado:
            total_a_pagar += (registro.total_trabalhado.total_seconds() / 3600) * valor_hora

    # Obter a lista de usuários para o filtro
    usuarios = CustomUser.objects.all()

    # Exibir informações de caixa para cada registro


    context = {
        'registros': registros,
        'usuarios': usuarios,
        'usuario_id': usuario_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'valor_hora': valor_hora,
        'total_a_pagar': total_a_pagar,
    }
    
    return TemplateResponse(request, 'core/consulta_pontos.html', context)

@login_required
def registrar_ponto(request):
    ip_requisitante = request.META.get('REMOTE_ADDR')
    print(ip_requisitante)
    # Verificar se o IP da requisição é o IP permitido
    if ip_requisitante not in settings.ALLOWED_IP:
        return HttpResponseForbidden("IP não autorizado para registrar ponto.")
    
    user = request.user

    if user.primeiro_acesso:
        return redirect('trocar-senha')

    registros = RegistroPonto.objects.filter(usuario=request.user).order_by('-data', '-entrada')

    if request.method == "POST":
        valor_em_caixa = request.POST.get("valor_em_caixa")
        valor_em_caixa = valor_em_caixa.replace('.', '').replace('R$ ', '').replace(',', '.')

        # Valida se o valor em caixa foi informado
        if not valor_em_caixa or not valor_em_caixa.replace('.', '', 1).isdigit():
            messages.error(request, "Você deve informar um valor válido em caixa!")
            return redirect('registrar-ponto')

        valor_em_caixa = float(valor_em_caixa)

        ultimo_registro = registros.first()

        if "entrada" in request.POST:
            # Verifica se já existe um registro de entrada para hoje
            if ultimo_registro and ultimo_registro.entrada and not ultimo_registro.saida and ultimo_registro.data == date.today():
                messages.error(request, "Você já registrou a entrada hoje e ainda não registrou a saída.")
                return redirect('registrar-ponto')

            RegistroPonto.objects.create(
                usuario=request.user,
                entrada=datetime.now().time(),
                valor_em_caixa_entrada=valor_em_caixa,
            )
            messages.success(request, "Entrada registrada com sucesso!")
            return redirect('registrar-ponto')

        elif "saida" in request.POST:
            # Verifica se já existe um registro de entrada sem saída
            if not ultimo_registro or not ultimo_registro.entrada or ultimo_registro.saida:
                messages.error(request, "Você não pode registrar uma saída sem antes registrar uma entrada.")
                return redirect('registrar-ponto')

            ultimo_registro.saida = datetime.now().time()
            ultimo_registro.valor_em_caixa_saida = valor_em_caixa
            ultimo_registro.save()

            messages.success(request, "Saída registrada com sucesso!")
            return redirect('registrar-ponto')
        
    registro_atual = registros.filter(data=date.today(), entrada__isnull=False, saida__isnull=True).first()
    # Passe `registro_atual` no contexto
    return render(request, 'core/registrar_ponto.html', {'registros': registros, 'registro_atual': registro_atual})

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

        return redirect('painel-mobile')  # Redireciona para a página de finalização de venda ou outra página relevante

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
                    if item_estoque.nome in [':Folha A4', '.Impressão (1 lado)', '.Impressão (2 lados)', 'Desperdício']:
                        # Abate a quantidade vendida do estoque dos três itens

                        for nome_item in [':Folha A4', '.Impressão (1 lado)', '.Impressão (2 lados)', 'Desperdício']:
                            item_associado = ItemEstoque.objects.get(nome=nome_item)
                            print(item_associado.nome)
                            if item_associado.quantidade >= quantidade_vendida:
                                item_associado.quantidade -= quantidade_vendida
                                item_associado.save()
                            else:
                                messages.error(request, f"Quantidade insuficiente no estoque para {nome_item}.")
                                return redirect('painel-vendas')
                    else:
                        # Verifica se há estoque suficiente
                        if item_estoque.quantidade >= quantidade_vendida:
                            item_estoque.quantidade -= quantidade_vendida
                            item_estoque.save()
                        else:
                            messages.error(request, f"Quantidade insuficiente no estoque para {item_estoque.nome}.")
                            return redirect('painel-vendas')

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
                return redirect('painel-vendas')

            return redirect('painel-vendas')  # Ou para onde você quiser redirecionar após a venda ser concluída

    return render(request, 'core/painel_vendas.html', {'carrinho': carrinho})

@login_required
def painel_vendas(request):
    # Obtém ou cria o carrinho ativo do usuário
    user = request.user

    if user.primeiro_acesso:
        return redirect('trocar-senha')
    
    else:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_parsed = parse(user_agent)

        # Verifica se o usuário está acessando pelo celular
        if user_agent_parsed.is_mobile:
            # Redireciona para a nova página para dispositivos móveis
            return redirect('painel-mobile')

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
            # Salva os dados do cliente no banco
            form.save()

            # Define o cookie "email_cadastrado" para garantir que o formulário não será mostrado novamente
            response = redirect('listar-estoque')  # Volta para a página de estoque

            # Define o cookie "email_cadastrado" por 1 ano
            response.set_cookie('email_cadastrado', 'true', max_age=60*60*24*365)
            messages.success(request, "Cadastro feito com sucesso!")
            return response
    else:
        form = ClienteForm()
      
    response = redirect('listar-estoque')
    return response
    
@user_passes_test(is_admin)
def usuarios(request):
    
    if request.user.primeiro_acesso:
        return redirect('trocar-senha')
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('usuarios')
    else:
        form = CustomUserCreationForm()

    users = get_user_model().objects.all()

    return TemplateResponse(request, 'core/usuarios.html', {'form': form, 'users': users})

@user_passes_test(is_admin)
def excluir_usuario(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('usuarios')
    
    return render(request, 'core/excluir_usuario.html', {'user': user})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('usuarios')
            else:
                return redirect('painel-vendas')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

            itens = ItemEstoque.objects.annotate(
                esgotado=Case(
                    When(quantidade=0, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ).order_by('-prioridade', 'esgotado', 'nome')

            agora = timezone.now()
            avisos_ativos = Aviso.objects.filter(data_inicio__lte=agora, data_fim__gte=agora)
            
            return TemplateResponse(request, 'core/estoque/listar_estoque.html', {'itens': itens, 'avisos_ativos': avisos_ativos})
    
    itens = ItemEstoque.objects.annotate(
        esgotado=Case(
            When(quantidade=0, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('-prioridade', 'esgotado', 'nome')

    agora = timezone.now()
    avisos_ativos = Aviso.objects.filter(data_inicio__lte=agora, data_fim__gte=agora)
    
    aberta = papelaria_aberta()
    horarios = HorarioFuncionamento.objects.all().order_by('dia_semana', 'abertura')
    for horario in horarios:
        horario.abertura = horario.abertura.strftime('%H:%M')
        horario.fechamento = horario.fechamento.strftime('%H:%M')

    return TemplateResponse(request, 'core/estoque/listar_estoque.html', {
        'itens': itens,
        'avisos_ativos': avisos_ativos,
        'papelaria_aberta': aberta,
        'horarios': horarios
    })

@user_passes_test(is_admin)
def admin_dashboard_clientes(request):

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

    return TemplateResponse(request, 'core/admin_dashboard_clientes.html', {'clientes': clientes})

@login_required
def user_dashboard(request):
    return render(request, 'core/user_dashboard.html')

@user_passes_test(is_admin)
def listar_estoque_admin(request):
    itens = ItemEstoque.objects.annotate(
        esgotado=Case(
            When(quantidade=0, then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('esgotado', '-prioridade', 'nome')
    
    return TemplateResponse(request, 'core/estoque/listar_estoque_admin.html', {'itens': itens})

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
        return redirect('listar-estoque-admin')

    return render(request, 'core/estoque/remover_item.html', {'item': item})    

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
                return redirect('listar-estoque')  # Redireciona para a página de sua escolha
            else:
                messages.error(request, 'Por favor, corrija os erros abaixo.')
        else:
            form = NovoPasswordForm(user)

        return TemplateResponse(request, 'core/trocar_senha.html', {'form': form})

    else:
        return redirect('listar-estoque')  # Se não for primeiro acesso, redireciona para outra página

def listar_estoque(request):
    itens = ItemEstoque.objects.annotate(
        esgotado=Case(
            When(quantidade=0, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('-prioridade', 'esgotado', 'nome')

    agora = timezone.now()
    avisos_ativos = Aviso.objects.filter(data_inicio__lte=agora, data_fim__gte=agora)
    
    aberta = papelaria_aberta()
    horarios = HorarioFuncionamento.objects.all().order_by('dia_semana', 'abertura')
    for horario in horarios:
        horario.abertura = horario.abertura.strftime('%H:%M')
        horario.fechamento = horario.fechamento.strftime('%H:%M')

    data_atual = timezone.now().date()

    # Verifica se já existe um registro de visita para a data atual
    visita, created = Visita.objects.get_or_create(data=data_atual)

    # Incrementa a contagem de visitas
    visita.contagem += 1
    visita.save()

    # Obtém a contagem total de visitas
    total_visitas = Visita.objects.aggregate(total=models.Sum('contagem'))['total']

    return TemplateResponse(request, 'core/estoque/listar_estoque.html', {
        'itens': itens,
        'avisos_ativos': avisos_ativos,
        'papelaria_aberta': aberta,
        'horarios': horarios,
        'total_visitas': total_visitas
    })

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