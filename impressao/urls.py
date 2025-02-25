from django.urls import path
from . import views

app_name = 'impressao'

urlpatterns = [
    path('enviar/', views.enviar_documento, name='enviar_documento'),
    path('fila/', views.documentos_fila, name='documentos_fila'),
    path('visualizar/<int:pk>/', views.visualizar_documento, name='visualizar_documento'),
    path('marcar_como_impresso/<int:pk>/', views.marcar_como_impresso, name='marcar_como_impresso'),
    path('consultar/', views.consultar_impressoes, name='consultar_impressoes'),
]