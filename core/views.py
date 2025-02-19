from estoque.models import ItemEstoque
from avisos.models import Aviso
from horarios.models import HorarioFuncionamento
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
from django.template.response import TemplateResponse
from django.db.models import Case, When, IntegerField
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Visita
from core.utils import papelaria_aberta

def home(request):
    # Anota os itens do estoque com um campo 'esgotado' baseado na quantidade
    itens = ItemEstoque.objects.annotate(
        esgotado=Case(
            When(quantidade=0, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('-prioridade', 'esgotado', 'nome')

    agora = timezone.now()
    # Filtra avisos ativos com base na data atual
    avisos_ativos = Aviso.objects.filter(data_inicio__lte=agora, data_fim__gte=agora)
    
    # Verifica se a papelaria está aberta
    aberta = papelaria_aberta()
    # Obtém todos os horários de funcionamento ordenados por dia da semana e horário de abertura
    horarios = HorarioFuncionamento.objects.all().order_by('dia_semana', 'abertura')
    for horario in horarios:
        # Formata os horários de abertura e fechamento
        horario.abertura = horario.abertura.strftime('%H:%M')
        horario.fechamento = horario.fechamento.strftime('%H:%M')

    data_atual = timezone.now().date()

    # Obtém ou cria um registro de visita para a data atual
    visita, created = Visita.objects.get_or_create(data=data_atual)

    ultima_visita = request.COOKIES.get('ultima_visita')
    
    # Verifica se a última visita foi há mais de uma hora
    if not ultima_visita or (timezone.now() - datetime.fromisoformat(ultima_visita)) > timedelta(hours=1):
        # Incrementa a contagem de visitas e salva
        visita.contagem += 1
        visita.save()

        # Calcula o total de visitas
        total_visitas = Visita.objects.aggregate(total=models.Sum('contagem'))['total']
        response = TemplateResponse(request, 'home.html', {
            'itens': itens,
            'avisos_ativos': avisos_ativos,
            'papelaria_aberta': aberta,
            'horarios': horarios,
            'total_visitas': total_visitas
        })
        # Define um cookie para registrar a última visita
        response.set_cookie('ultima_visita', timezone.now().isoformat(), max_age=3600)
        return response

    # Calcula o total de visitas
    total_visitas = Visita.objects.aggregate(total=models.Sum('contagem'))['total']

    return TemplateResponse(request, 'home.html', {
        'itens': itens,
        'avisos_ativos': avisos_ativos,
        'papelaria_aberta': aberta,
        'horarios': horarios,
        'total_visitas': total_visitas
    })


def custom_logout(request):
    # Limpa a sessão e faz logout do usuário
    request.session.flush()
    auth_logout(request)
    return redirect('core:login')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')
        # Autentica o usuário
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Faz login do usuário
            login(request, user)
            
            # Define a expiração da sessão com base na opção 'remember_me'
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                request.session.set_expiry(0)

            # Redireciona o usuário com base no tipo de usuário
            if user.is_superuser:
                return redirect('usuarios:usuarios')
            else:
                return redirect('vendas:painel-vendas')
        else:
            # Exibe mensagem de erro se a autenticação falhar
            messages.error(request, 'Usuário ou senha inválidos.')

            return redirect('core:home')
        
    return redirect('core:home')
