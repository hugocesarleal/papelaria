from django.db import models
from django.conf import settings

class DocumentoImpressao(models.Model):
    nome_cliente = models.CharField(max_length=255)
    documento = models.FileField(upload_to='documentos/')
    impresso = models.BooleanField(default=False)
    data_envio = models.DateTimeField(auto_now_add=True)
    usuario_impresso = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.nome_cliente