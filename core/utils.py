from django.utils import timezone
from horarios.models import HorarioFuncionamento, ExcecaoHorario

# Função que verifica se o usuário é um administrador
def is_admin(user):
    return user.is_staff

# Função que verifica se a papelaria está aberta
def papelaria_aberta():
    # Obtém a hora atual e o dia da semana atual
    hora_atual = timezone.localtime(timezone.now()).time()
    dia_semana_atual = timezone.localtime(timezone.now()).weekday()

    # Filtra os horários de funcionamento para o dia da semana atual
    horarios = HorarioFuncionamento.objects.filter(dia_semana=dia_semana_atual)
    # Filtra as exceções de horário para a data atual
    excecoes = ExcecaoHorario.objects.filter(data=timezone.localtime(timezone.now()).date())

    # Verifica se a hora atual está dentro de algum horário de funcionamento
    for horario in horarios:
        if horario.abertura <= hora_atual <= horario.fechamento:
            # Verifica se há alguma exceção para o horário atual
            for excecao in excecoes:
                if excecao.horario == horario:
                    return False
            return True
    return False