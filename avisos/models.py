from django.db import models
from django.conf import settings

class Aviso(models.Model):
    texto = models.TextField()
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()

    def __str__(self):
        return f"Aviso: {self.texto[:50]}"

class AvisoVisualizado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE)
    data_visualizado = models.DateTimeField(auto_now_add=True)