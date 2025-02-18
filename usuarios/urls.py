from django.urls import path, include
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.usuarios, name='usuarios'),
    path('usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir-usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar-usuario'),
    path('trocar-senha/', views.trocar_senha, name='trocar-senha'),
]