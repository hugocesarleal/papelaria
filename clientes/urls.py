from django.urls import path, include
from . import views

app_name = 'clientes'

urlpatterns = [
    path('cadastrar-cliente/', views.cadastrar_cliente, name='cadastrar-cliente'),
    path('', views.admin_dashboard_clientes, name='admin-clientes'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar-cliente'),
    path('clientes/excluir/<int:pk>/', views.excluir_cliente, name='excluir-cliente'),
]