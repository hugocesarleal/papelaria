from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.listar_estoque, name='listar-estoque'),
    path('login/', views.login_view, name='login'),
    path('user-dashboard/', views.painel_vendas, name='painel-vendas'),
    path('logout/', views.custom_logout, name='logout'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('estoque/', views.listar_estoque_admin, name='listar-estoque-admin'),
    path('estoque/adicionar/', views.adicionar_item, name='adicionar-item'),
    path('estoque/editar/<int:pk>/', views.editar_item, name='editar-item'),
    path('estoque/remover/<int:pk>/', views.remover_item, name='remover-item'),
    path('cadastrar-cliente/', views.cadastrar_cliente, name='cadastrar-cliente'),
    path('admin-dashboard-clientes/', views.admin_dashboard_clientes, name='admin-dashboard-clientes'),
    path('concluir-venda/', views.concluir_venda, name='concluir-venda'),
    path('buscar-itens/', views.buscar_itens, name='buscar-itens'),
    path('remover-item-carrinho/<int:item_id>/', views.remover_item_carrinho, name='remover-item-carrinho'),
    path('limpar-carrinho/', views.limpar_carrinho, name='limpar-carrinho'),
    path('painel-mobile/', views.upload_comprovante, name='painel-mobile'),
    path('buscar-comprovantes-pix/<int:carrinho_id>/', views.buscar_comprovantes, name='buscar-comprovantes-pix'),
    path('consulta-pontos/', views.consulta_pontos, name='consulta_pontos'),
    path('registrar-ponto/', views.registrar_ponto, name='registrar-ponto'),
    path('vendas-admin/', views.vendas_admin, name='vendas-admin'),
    path('avisos/', views.listar_avisos, name='listar-avisos'),
    path('avisos/editar/<int:pk>/', views.editar_aviso, name='editar-aviso'),
    path('avisos/excluir/<int:pk>/', views.excluir_aviso, name='excluir-aviso'),
    path('trocar-senha/', views.trocar_senha, name='trocar-senha'),
    path('usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir-usuario'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar-cliente'),
    path('clientes/excluir/<int:pk>/', views.excluir_cliente, name='excluir-cliente'),
    path('horarios/', views.gerenciar_horarios, name='gerenciar-horarios'),
    path('horarios/editar/<int:pk>/', views.editar_horario, name='editar-horario'),
    path('horarios/excluir/<int:pk>/', views.excluir_horario, name='excluir-horario'),
    path('excecoes/editar/<int:pk>/', views.editar_excecao, name='editar-excecao'),
    path('excecoes/excluir/<int:pk>/', views.excluir_excecao, name='excluir-excecao'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar-usuario'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('save_question/', views.save_question, name='save_question'),
    path('responder-duvidas/', views.responder_duvidas, name='responder_duvidas'),
]