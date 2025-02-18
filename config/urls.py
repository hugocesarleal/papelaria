"""pypel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include  # Importando 'include' corretamente
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('avisos/', include('avisos.urls', namespace='avisos')),
    path('duvidas/', include('duvidas.urls', namespace='duvidas')),
    path('estoque/', include('estoque.urls', namespace='estoque')),
    path('horarios/', include('horarios.urls', namespace='horarios')),
    path('pontos/', include('pontos.urls', namespace='pontos')),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('vendas/', include('vendas.urls', namespace='vendas')),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('', include('core.urls', namespace='core')),  # Mantenha o core se ainda houver conteúdo nele
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

