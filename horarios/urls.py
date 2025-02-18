from django.urls import path, include
from . import views

app_name = 'horarios'

urlpatterns = [
    path('', views.gerenciar_horarios, name='gerenciar-horarios'),
    path('horarios/editar/<int:pk>/', views.editar_horario, name='editar-horario'),
    path('horarios/excluir/<int:pk>/', views.excluir_horario, name='excluir-horario'),
    path('excecoes/editar/<int:pk>/', views.editar_excecao, name='editar-excecao'),
    path('excecoes/excluir/<int:pk>/', views.excluir_excecao, name='excluir-excecao'),
]