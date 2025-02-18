from django.shortcuts import render
from .models import Duvida
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import difflib
import re
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ResponderDuvidaForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template.response import TemplateResponse

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def responder_duvidas(request):
    duvidas = Duvida.objects.filter(respondida=False)
    if request.method == 'POST':
        form = ResponderDuvidaForm(request.POST)
        if form.is_valid():
            duvida_id = request.POST.get('duvida_id')
            duvida = get_object_or_404(Duvida, id=duvida_id)
            duvida.resposta = form.cleaned_data['resposta']
            duvida.respondida = True
            duvida.save()
            # Enviar email para o cliente
            subject = 'Resposta à sua dúvida'
            message = f"""
            Olá {duvida.nome},

            Você nos enviou a seguinte dúvida:
            {duvida.mensagem}

            Nossa resposta:
            {duvida.resposta}

            Se você tiver mais alguma dúvida, não hesite em nos contatar.

            Atenciosamente,
            Equipe Papelaria
            """
            try:
                send_mail(
                    subject,
                    message,
                    'admin@papelaria.com',
                    [duvida.email],
                    fail_silently=False,
                )
            except BadHeaderError:
                messages.error(request, 'Erro ao enviar o email. A dúvida foi marcada como respondida, mas o email não pôde ser enviado.')
                return redirect('duvidas:responder_duvidas')
            except Exception as e:
                messages.error(request, f'Erro ao enviar o email. A dúvida foi marcada como respondida, mas o email não pôde ser enviado.')
                return redirect('duvidas:responder_duvidas')

            messages.success(request, 'Dúvida respondida e email enviado com sucesso.')
            return redirect('duvidas:responder_duvidas')
    else:
        form = ResponderDuvidaForm()
    return TemplateResponse(request, 'responder_duvidas.html', {'duvidas': duvidas, 'form': form})

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').lower()

        # Respostas padronizadas
        respostas = {
            'horário de funcionamento': '🕒 Consulte nossos horários de funcionamento clicando no ícone no menu lateral ou superior.',
            'abrem': '🕒 Consulte nossos horários de funcionamento clicando no ícone no menu lateral ou superior.',
            'horas': '🕒 Consulte nossos horários de funcionamento clicando no ícone no menu lateral ou superior.',
            'horário': '🕒 Consulte nossos horários de funcionamento clicando no ícone no menu lateral ou superior.',
            'horários': '🕒 Consulte nossos horários de funcionamento clicando no ícone no menu lateral ou superior.',
            'abre': '🕒 Consulte nossos horários de funcionamento clicando no ícone no menu lateral ou superior.',
            'abrir': '🕒 Consulte nossos horários de funcionamento clicando no ícone no menu lateral ou superior.',
            'aberto': '🔓 Para saber se a papelaria está aberta, basta conferir o aviso no canto superior direito da página.',
            'endereço': '📍 Estamos localizados no prédio do DCE, ao lado da biblioteca.',
            'localização': '📍 Estamos localizados no prédio do DCE, ao lado da biblioteca.',
            'valores': '💲 Os valores dos itens vendidos podem ser consultados na página inicial.',
            'valor': '💲 Os valores dos itens vendidos podem ser consultados na página inicial.',
            'preços': '💲 Os valores dos itens vendidos podem ser consultados na página inicial.',
            'preço': '💲 Os valores dos itens vendidos podem ser consultados na página inicial.',
            'contato': '📧 Você pode nos contatar pelo email dce.guytorres@gmail.com.',
            'email': '📧 Você pode nos contatar pelo email dce.guytorres@gmail.com.',
            'formas de pagamento': '💵 Aceitamos pagamentos em dinheiro e PIX.',
            'dinheiro': '💵 Aceitamos pagamentos em dinheiro e PIX.',
            'pix': '💵 Aceitamos pagamentos em dinheiro e PIX.',
            'cartão': '💵 Aceitamos pagamentos em dinheiro e PIX.',
            'promoções': '🎉 Cadastre seu email no site para saber sobre promoções e descontos.',
            'promoção': '🎉 Cadastre seu email no site para saber sobre promoções e descontos.',
            'ajuda': '❓ Se tiver alguma dúvida, entre em contato conosco pelo email dce.guytorres@gmail.com.',
            'duvida': '❓ Se tiver alguma dúvida, entre em contato conosco pelo email dce.guytorres@gmail.com.'
        }

        # Verifica se a mensagem contém alguma palavra-chave ou similar
        for chave, resposta in respostas.items():
            if re.search(r'\b' + re.escape(chave) + r'\b', message):
                return JsonResponse({'response': resposta})

        # Filtragem com difflib para encontrar a resposta mais próxima
        palavras_chave = list(respostas.keys())
        melhor_correspondencia = difflib.get_close_matches(message, palavras_chave, n=1, cutoff=0.6)
        if melhor_correspondencia:
            return JsonResponse({'response': respostas[melhor_correspondencia[0]]})

        return JsonResponse({'response': None})
    return JsonResponse({'response': 'Método não permitido.'}, status=405)

@csrf_exempt
def save_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')

            # Verifica se os dados foram recebidos corretamente
            if not name or not email or not message:
                return JsonResponse({'success': False, 'error': 'Dados incompletos'}, status=400)

            # Salva a dúvida no banco de dados
            duvida = Duvida(nome=name, email=email, mensagem=message)
            duvida.save()

            # Enviar notificação para o administrador
            subject = 'Nova dúvida registrada'
            notification_message = f"""
            Uma nova dúvida foi registrada no sistema.

            Nome: {name}
            Email: {email}
            Mensagem: {message}

            Acesse o painel de administração para responder a dúvida.
            """
            send_mail(
                subject,
                notification_message,
                'dce.guytorres@gmail.com',
                ['hugocesarleal@gmail.com'],
                fail_silently=False,
            )

            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Erro ao decodificar JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)