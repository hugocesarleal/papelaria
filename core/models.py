from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class ItemEstoque(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    foto = models.ImageField(upload_to='estoque/', null=False, default='path/to/default/image.jpg')  # Definindo uma imagem padrão
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField()

    def __str__(self):
        return self.nomes

class Carrinho(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Atualiza para usar o modelo de usuário configurado
    ativo = models.BooleanField(default=True)
    comprovante_pix = models.ImageField(upload_to='comprovantes_pix/', null=True, blank=True)

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

    def __str__(self):
        return self.username
