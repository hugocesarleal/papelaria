from django.shortcuts import render, get_object_or_404, redirect
from .models import Cliente
from .forms import ClienteForm
from django.contrib import messages
from django.core.paginator import Paginator
from core.utils import is_admin
from django.template.response import TemplateResponse
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(is_admin)
def admin_dashboard_clientes(request):
    clientes = Cliente.objects.all()

    nome_cliente = request.GET.get('nome_cliente')
    if (nome_cliente):
        clientes = clientes.filter(nome__icontains=nome_cliente)

    paginator = Paginator(clientes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if (request.method == "POST"):
        assunto = request.POST.get("assunto")
        mensagem = request.POST.get("mensagem")
        destinatarios = [cliente.email for cliente in clientes]
        arquivos = request.FILES.getlist('arquivos')

        if (assunto and mensagem):
            email = EmailMessage(
                subject=assunto,
                body=mensagem,
                from_email='seu_email@dominio.com',
            )
            email.bcc = destinatarios
            
            for arquivo in arquivos:
                email.attach(arquivo.name, arquivo.read(), arquivo.content_type)

            email.send(fail_silently=False)
            return redirect('clientes:admin-clientes')

    return TemplateResponse(request, 'admin_dashboard_clientes.html', {'clientes': page_obj})

@user_passes_test(is_admin)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if (request.method == 'POST'):
        form = ClienteForm(request.POST, instance=cliente)
        if (form.is_valid()):
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes:admin-clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'editar_cliente.html', {'form': form, 'cliente': cliente})

@user_passes_test(is_admin)
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if (request.method == 'POST'):
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('admin-dashboard-clientes')
    
    return render(request, 'excluir_cliente.html', {'cliente': cliente})

def cadastrar_cliente(request):
    if (request.method == 'POST'):
        form = ClienteForm(request.POST)
        if (form.is_valid()):
            form.save()
            response = redirect('core:home')
            response.set_cookie('email_cadastrado', 'true', max_age=60*60*24*365)
            messages.success(request, "Cadastro feito com sucesso!")
            return response
    else:
        form = ClienteForm()
      
    response = redirect('core:home')
    return response
