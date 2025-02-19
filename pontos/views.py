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
    # Verifica se o método da requisição é POST e se o botão 'atualizar_valor_hora' foi pressionado
    if request.method == 'POST' and 'atualizar_valor_hora' in request.POST:
        # Obtém o novo valor da hora a partir do formulário e formata o valor
        novo_valor_hora = request.POST.get('valor_hora')
        novo_valor_hora = novo_valor_hora.replace('.', '').replace('R$ ', '').replace(',', '.')

        try:
            # Tenta obter a configuração existente e atualizar o valor da hora
            configuracao = Configuracao.objects.get(id=1)
            configuracao.valor_hora = Decimal(novo_valor_hora)
            configuracao.save()
        except Configuracao.DoesNotExist:
            # Se a configuração não existir, cria uma nova
            Configuracao.objects.create(valor_hora=Decimal(novo_valor_hora))

        # Adiciona uma mensagem de sucesso
        messages.success(request, 'Valor da hora atualizado com sucesso!')

    # Verifica se o botão 'limpar_filtros' foi pressionado
    if 'limpar_filtros' in request.GET:
        return redirect('pontos:consulta_pontos')

    # Obtém os filtros da requisição GET
    usuario_id = request.GET.get('usuario', None)
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)

    # Obtém o valor da hora a partir da configuração
    valor_hora = Configuracao.get_valor_hora()

    try:
        # Tenta converter o valor da hora para float
        valor_hora = float(valor_hora)
    except ValueError:
        valor_hora = 0.0

    # Obtém todos os registros de ponto
    registros = RegistroPonto.objects.all()

    # Aplica os filtros aos registros
    if usuario_id:
        registros = registros.filter(usuario_id=usuario_id)
    if data_inicio:
        registros = registros.filter(data__gte=data_inicio)
    if data_fim:
        registros = registros.filter(data__lte=data_fim)

    # Ordena os registros por data e entrada
    registros = registros.order_by('-data', '-entrada')

    # Paginação dos registros
    paginator = Paginator(registros, 10)
    page_number = request.GET.get('page')
    registros_page = paginator.get_page(page_number)

    # Calcula o total a pagar
    total_a_pagar = 0
    if usuario_id or data_inicio or data_fim:
        for registro in registros:
            if registro.total_trabalhado:
                horas_trabalhadas = registro.total_trabalhado.total_seconds() / 3600
                total_a_pagar += horas_trabalhadas * valor_hora

    # Obtém todos os usuários
    usuarios = CustomUser.objects.all()

    # Contexto para renderização do template
    context = {
        'registros': registros_page,
        'usuarios': usuarios,
        'usuario_id': usuario_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'valor_hora': valor_hora,
        'total_a_pagar': total_a_pagar if (usuario_id or data_inicio or data_fim) else None,
    }

    # Renderiza o template com o contexto
    return TemplateResponse(request, 'consulta_pontos.html', context)

@login_required
def registrar_ponto(request):
    # Obtém o IP do requisitante
    ip_requisitante = request.META.get('REMOTE_ADDR')

    # Verifica se o IP da requisição é o IP permitido
    # if ip_requisitante not in settings.ALLOWED_IP:
    #     messages.error(request, "Dispositivo não autorizado para registrar ponto.")
    #     return redirect('vendas:painel-vendas')

    user = request.user

    # Redireciona o usuário para trocar a senha se for o primeiro acesso
    if user.primeiro_acesso:
        return redirect('usuarios:trocar-senha')

    # Obtém os registros de ponto do usuário ordenados por data e entrada
    registros = RegistroPonto.objects.filter(usuario=request.user).order_by('-data', '-entrada')

    if request.method == "POST":
        # Obtém o valor em caixa a partir do formulário e formata o valor
        valor_em_caixa = request.POST.get("valor_em_caixa")
        valor_em_caixa = valor_em_caixa.replace('.', '').replace('R$ ', '').replace(',', '.')

        # Verifica se o valor em caixa é válido
        if not valor_em_caixa or not valor_em_caixa.replace('.', '', 1).isdigit():
            messages.error(request, "Você deve informar um valor válido em caixa!")
            return redirect('pontos:registrar-ponto')

        valor_em_caixa = float(valor_em_caixa)

        # Obtém o último registro de ponto do usuário
        ultimo_registro = registros.first()

        if "entrada" in request.POST:
            # Verifica se o usuário já registrou a entrada hoje e ainda não registrou a saída
            if ultimo_registro and ultimo_registro.entrada and not ultimo_registro.saida and ultimo_registro.data == date.today():
                messages.error(request, "Você já registrou a entrada hoje e ainda não registrou a saída.")
                return redirect('pontos:registrar-ponto')

            # Cria um novo registro de entrada
            RegistroPonto.objects.create(
                usuario=request.user,
                entrada=datetime.now().time(),
                valor_em_caixa_entrada=valor_em_caixa,
            )
            messages.success(request, "Entrada registrada com sucesso!")
            return redirect('pontos:registrar-ponto')

        elif "saida" in request.POST:
            # Verifica se o usuário pode registrar uma saída
            if not ultimo_registro or not ultimo_registro.entrada or ultimo_registro.saida:
                messages.error(request, "Você não pode registrar uma saída sem antes registrar uma entrada.")
                return redirect('pontos:registrar-ponto')

            # Atualiza o registro de ponto com a saída
            ultimo_registro.saida = datetime.now().time()
            ultimo_registro.valor_em_caixa_saida = valor_em_caixa
            ultimo_registro.save()

            messages.success(request, "Saída registrada com sucesso!")
            return redirect('pontos:registrar-ponto')

    # Obtém o registro atual do dia, se existir
    registro_atual = registros.filter(data=date.today(), entrada__isnull=False, saida__isnull=True).first()
    return render(request, 'registrar_ponto.html', {'registros': registros, 'registro_atual': registro_atual})
