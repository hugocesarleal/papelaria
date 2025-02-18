from django.urls import path, include
from . import views

app_name = 'duvidas'

urlpatterns = [
    path('', views.responder_duvidas, name='responder_duvidas'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('save_question/', views.save_question, name='save_question'),
]