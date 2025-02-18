from django.utils import timezone
from horarios.models import HorarioFuncionamento, ExcecaoHorario

def is_admin(user):
    return user.is_staff

def papelaria_aberta():
    hora_atual = timezone.localtime(timezone.now()).time()
    dia_semana_atual = timezone.localtime(timezone.now()).weekday()

    horarios = HorarioFuncionamento.objects.filter(dia_semana=dia_semana_atual)
    excecoes = ExcecaoHorario.objects.filter(data=timezone.localtime(timezone.now()).date())

    for horario in horarios:
        if horario.abertura <= hora_atual <= horario.fechamento:
            for excecao in excecoes:
                if excecao.horario == horario:
                    return False
            return True
    return False