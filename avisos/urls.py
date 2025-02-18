from django.urls import path, include
from . import views

app_name = 'avisos'

urlpatterns = [
    path('', views.listar_avisos, name='listar-avisos'),
    path('avisos/editar/<int:pk>/', views.editar_aviso, name='editar-aviso'),
    path('avisos/excluir/<int:pk>/', views.excluir_aviso, name='excluir-aviso'),
]