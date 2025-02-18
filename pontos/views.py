from django.shortcuts import render
from .models import RegistroPonto, Configuracao
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.core.paginator import Paginator
from datetime import datetime, date
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import CustomUser
from django.conf import settings
from decimal import Decimal
from core.utils import is_admin

@user_passes_test(is_admin)
def consulta_pontos(request):
    # Verifica se o formulário foi enviado para atualizar o valor da hora
    if request.method == 'POST' and 'atualizar_valor_hora' in request.POST:
        novo_valor_hora = request.POST.get('valor_hora')
        # Corrige o formato do valor da hora (substituindo vírgula por ponto)
        novo_valor_hora = novo_valor_hora.replace('.', '').replace('R$ ', '').replace(',', '.')
        
        try:
            configuracao = Configuracao.objects.get(id=1)
            configuracao.valor_hora = Decimal(novo_valor_hora)
            configuracao.save()
        except Configuracao.DoesNotExist:
            Configuracao.objects.create(valor_hora=Decimal(novo_valor_hora))

        messages.success(request, 'Valor da hora atualizado com sucesso!')

    # Se o botão de "Limpar Filtros" for pressionado, limpa os filtros
    if 'limpar_filtros' in request.GET:
        return redirect('pontos:consulta_pontos')  # Redireciona para a página de consulta sem filtros aplicados

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

    # Paginação
    paginator = Paginator(registros, 10)  # Mostra 10 registros por página
    page_number = request.GET.get('page')
    registros_page = paginator.get_page(page_number)

    # Calculando o total a pagar para o usuário selecionado
    total_a_pagar = 0
    if usuario_id or data_inicio or data_fim:
        for registro in registros:
            if registro.total_trabalhado:
                horas_trabalhadas = registro.total_trabalhado.total_seconds() / 3600
                total_a_pagar += horas_trabalhadas * valor_hora

    # Obter a lista de usuários para o filtro
    usuarios = CustomUser.objects.all()

    context = {
        'registros': registros_page,
        'usuarios': usuarios,
        'usuario_id': usuario_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'valor_hora': valor_hora,
        'total_a_pagar': total_a_pagar if (usuario_id or data_inicio or data_fim) else None,
    }

    return TemplateResponse(request, 'consulta_pontos.html', context)

@login_required
def registrar_ponto(request):
    ip_requisitante = request.META.get('REMOTE_ADDR')
    #print(ip_requisitante)
    # Verificar se o IP da requisição é o IP permitido
    #if ip_requisitante not in settings.ALLOWED_IP:
        #messages.error(request, "Dispositivo não autorizado para registrar ponto.")
        #return redirect('vendas:painel-vendas')
    
    user = request.user

    if user.primeiro_acesso:
        return redirect('usuarios:trocar-senha')

    registros = RegistroPonto.objects.filter(usuario=request.user).order_by('-data', '-entrada')

    if request.method == "POST":
        valor_em_caixa = request.POST.get("valor_em_caixa")
        valor_em_caixa = valor_em_caixa.replace('.', '').replace('R$ ', '').replace(',', '.')

        # Valida se o valor em caixa foi informado
        if not valor_em_caixa or not valor_em_caixa.replace('.', '', 1).isdigit():
            messages.error(request, "Você deve informar um valor válido em caixa!")
            return redirect('pontos:registrar-ponto')

        valor_em_caixa = float(valor_em_caixa)

        ultimo_registro = registros.first()

        if "entrada" in request.POST:
            # Verifica se já existe um registro de entrada para hoje
            if ultimo_registro and ultimo_registro.entrada and not ultimo_registro.saida and ultimo_registro.data == date.today():
                messages.error(request, "Você já registrou a entrada hoje e ainda não registrou a saída.")
                return redirect('pontos:registrar-ponto')

            RegistroPonto.objects.create(
                usuario=request.user,
                entrada=datetime.now().time(),
                valor_em_caixa_entrada=valor_em_caixa,
            )
            messages.success(request, "Entrada registrada com sucesso!")
            return redirect('pontos:registrar-ponto')

        elif "saida" in request.POST:
            # Verifica se já existe um registro de entrada sem saída
            if not ultimo_registro or not ultimo_registro.entrada or ultimo_registro.saida:
                messages.error(request, "Você não pode registrar uma saída sem antes registrar uma entrada.")
                return redirect('pontos:registrar-ponto')

            ultimo_registro.saida = datetime.now().time()
            ultimo_registro.valor_em_caixa_saida = valor_em_caixa
            ultimo_registro.save()

            messages.success(request, "Saída registrada com sucesso!")
            return redirect('pontos:registrar-ponto')
        
    registro_atual = registros.filter(data=date.today(), entrada__isnull=False, saida__isnull=True).first()
    # Passe `registro_atual` no contexto
    return render(request, 'registrar_ponto.html', {'registros': registros, 'registro_atual': registro_atual})
