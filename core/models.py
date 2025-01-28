from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, date

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

class ItemEstoque(models.Model):
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='estoque/', null=False, default='path/to/default/image.jpg')  # Definindo uma imagem padrão
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField()

    def __str__(self):
        return self.nomes

class Carrinho(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Atualiza para usar o modelo de usuário configurado
    ativo = models.BooleanField(default=True)
    comprovante_pix = models.ImageField(upload_to='comprovantes_pix/', null=True, blank=True)
    data_venda = models.DateTimeField(null=True, blank=True)  # Data e hora da venda
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Valor total da venda

    def __str__(self):
        return f"Carrinho de {self.user.username}"

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, related_name='itens', on_delete=models.CASCADE)
    item_estoque = models.ForeignKey(ItemEstoque, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade} de {self.item_estoque.nome}"

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.nome

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    primeiro_acesso = models.BooleanField(default=True)

    def __str__(self):
        return self.username

