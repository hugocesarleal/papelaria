from django.db import models
from django.conf import settings
from estoque.models import ItemEstoque

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
