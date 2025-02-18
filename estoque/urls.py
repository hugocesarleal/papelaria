from django.urls import path, include
from . import views

app_name = 'estoque'

urlpatterns = [
    path('buscar-itens/', views.buscar_itens, name='buscar-itens'),
    path('', views.listar_estoque_admin, name='listar-estoque-admin'),
    path('estoque/adicionar/', views.adicionar_item, name='adicionar-item'),
    path('estoque/editar/<int:pk>/', views.editar_item, name='editar-item'),
    path('estoque/remover/<int:pk>/', views.remover_item, name='remover-item'),
]