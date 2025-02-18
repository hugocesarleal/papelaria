from django.db import models
from django.conf import settings
from datetime import datetime, date

class Configuracao(models.Model):
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Configuração global - Valor da hora: R$ {self.valor_hora}"

    @staticmethod
    def get_valor_hora():
        config, created = Configuracao.objects.get_or_create(id=1)
        return config.valor_hora

class RegistroPonto(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    entrada = models.TimeField(null=True, blank=True)
    saida = models.TimeField(null=True, blank=True)
    valor_em_caixa_entrada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_em_caixa_saida = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_trabalhado = models.DurationField(null=True, blank=True)

    def calcular_total_trabalhado(self):
        if self.entrada and self.saida:
            return datetime.combine(date.min, self.saida) - datetime.combine(date.min, self.entrada)
        return None

    def save(self, *args, **kwargs):
        self.total_trabalhado = self.calcular_total_trabalhado()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Registro de {self.usuario} em {self.data}"
