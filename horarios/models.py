from django.db import models

class HorarioFuncionamento(models.Model):
    DIA_SEMANA_CHOICES = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    dia_semana = models.IntegerField(choices=DIA_SEMANA_CHOICES)
    abertura = models.TimeField()
    fechamento = models.TimeField()

    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.abertura} às {self.fechamento}"

class ExcecaoHorario(models.Model):
    horario = models.ForeignKey(HorarioFuncionamento, on_delete=models.CASCADE, related_name="excecoes")
    data = models.DateField()  # A data da exceção
