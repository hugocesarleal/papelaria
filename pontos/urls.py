from django.urls import path, include
from . import views

app_name = 'pontos'

urlpatterns = [
    path('consulta-pontos/', views.consulta_pontos, name='consulta_pontos'),
    path('registrar-ponto/', views.registrar_ponto, name='registrar-ponto'),
]