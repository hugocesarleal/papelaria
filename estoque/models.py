from django.db import models

class ItemEstoque(models.Model):
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='estoque/', null=False, default='path/to/default/image.jpg')  # Definindo uma imagem padrão
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField()
    prioridade = models.BooleanField(default=False)  # Campo de prioridade

    def __str__(self):
        return self.nome
