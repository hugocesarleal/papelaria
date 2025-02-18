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

    # Verifica o cookie de última visita
    ultima_visita = request.COOKIES.get('ultima_visita')
    
    if not ultima_visita or (timezone.now() - datetime.fromisoformat(ultima_visita)) > timedelta(hours=1):
        # Incrementa a contagem de visitas
        visita.contagem += 1
        visita.save()

        total_visitas = Visita.objects.aggregate(total=models.Sum('contagem'))['total']
        # Define o cookie de última visita
        response = TemplateResponse(request, 'home.html', {
            'itens': itens,
            'avisos_ativos': avisos_ativos,
            'papelaria_aberta': aberta,
            'horarios': horarios,
            'total_visitas': total_visitas
        })
        response.set_cookie('ultima_visita', timezone.now().isoformat(), max_age=3600)
        return response

    # Obtém a contagem total de visitas
    total_visitas = Visita.objects.aggregate(total=models.Sum('contagem'))['total']

    return TemplateResponse(request, 'home.html', {
        'itens': itens,
        'avisos_ativos': avisos_ativos,
        'papelaria_aberta': aberta,
        'horarios': horarios,
        'total_visitas': total_visitas
    })


def custom_logout(request):
    request.session.flush()
    auth_logout(request)  # Isso faz o logout do usuário
    return redirect('core:login')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')  # Obtém o valor do checkbox
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if remember_me:
                # Define a duração da sessão para 30 dias
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                # Define a duração da sessão para o padrão (navegador fechado)
                request.session.set_expiry(0)

            if user.is_superuser:
                return redirect('usuarios:usuarios')
            else:
                return redirect('vendas:painel-vendas')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

            return redirect('core:home')
        
    return redirect('core:home')



