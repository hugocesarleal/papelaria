from django.urls import path, include
from . import views

app_name = 'vendas'

urlpatterns = [
    path('painel-vendas/', views.painel_vendas, name='painel-vendas'),
    path('', views.vendas_admin, name='vendas-admin'),
    path('painel-mobile/', views.upload_comprovante, name='painel-mobile'),
    path('buscar-comprovantes-pix/<int:carrinho_id>/', views.buscar_comprovantes, name='buscar-comprovantes-pix'),
    path('concluir-venda/', views.concluir_venda, name='concluir-venda'),
    path('remover-item-carrinho/<int:item_id>/', views.remover_item_carrinho, name='remover-item-carrinho'),
    path('limpar-carrinho/', views.limpar_carrinho, name='limpar-carrinho'),
]