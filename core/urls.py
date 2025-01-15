from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.listar_estoque, name='listar-estoque'),
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('user-dashboard/', views.painel_vendas, name='painel-vendas'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('create-user/', views.create_user, name='create-user'),
    path('user-list/', views.user_list, name='user-list'),
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
    path('nova-pagina/', views.upload_comprovante, name='nova-pagina'),
    path('buscar-comprovantes-pix/', views.buscar_comprovantes, name='buscar-comprovantes-pix'),
]
