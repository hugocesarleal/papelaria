from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DocumentoImpressao
from .forms import DocumentoImpressaoForm
from django.http import FileResponse
from django.template.response import TemplateResponse
import os
from django.conf import settings
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from docx import Document
import subprocess
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import user_passes_test
from core.utils import is_admin
from core.models import CustomUser

def enviar_documento(request):
    if request.method == 'POST':
        form = DocumentoImpressaoForm(request.POST)
        if form.is_valid():
            nome_cliente = form.cleaned_data['nome_cliente']
            arquivos = request.FILES.getlist('documentos')
            for uploaded_file in arquivos:
                if not (uploaded_file.name.endswith('.pdf') or uploaded_file.name.endswith('.docx') or uploaded_file.name.endswith('.doc')):
                    messages.error(request, 'Apenas arquivos PDF, DOC e DOCX são permitidos.')
                    return TemplateResponse(request, 'enviar_documento.html', {'form': form})
                documento = DocumentoImpressao(nome_cliente=nome_cliente)
                if not uploaded_file.name.endswith('.pdf'):
                    if uploaded_file.name.endswith('.docx') or uploaded_file.name.endswith('.doc'):
                        # Save the uploaded docx or doc temporarily
                        temp_doc_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
                        with open(temp_doc_path, 'wb') as temp_doc_file:
                            for chunk in uploaded_file.chunks():
                                temp_doc_file.write(chunk)
                        # Convert docx or doc to pdf using LibreOffice
                        temp_pdf_path = temp_doc_path.replace('.docx', '.pdf').replace('.doc', '.pdf')
                        libreoffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
                        subprocess.run([libreoffice_path, '--headless', '--convert-to', 'pdf', '--outdir', settings.MEDIA_ROOT, temp_doc_path])
                        with open(temp_pdf_path, 'rb') as temp_pdf_file:
                            documento.documento.save(f"{uploaded_file.name}.pdf", temp_pdf_file)
                        os.remove(temp_doc_path)  # Remove the temporary docx or doc file
                        os.remove(temp_pdf_path)  # Remove the temporary pdf file
                    else:
                        text = uploaded_file.read().decode('utf-8')
                        pdf_output = BytesIO()
                        c = canvas.Canvas(pdf_output, pagesize=A4)
                        text_lines = text.split('\n')
                        y = 750
                        for line in text_lines:
                            c.drawString(100, y, line)
                            y -= 15
                        c.showPage()
                        c.save()
                        pdf_output.seek(0)
                        documento.documento.save(f"{uploaded_file.name}.pdf", pdf_output)
                else:
                    documento.documento = uploaded_file
                documento.save()
            
            messages.success(request, 'Documento enviado com sucesso.')
            return redirect('impressao:enviar_documento')
    else:
        form = DocumentoImpressaoForm()
    return TemplateResponse(request, 'enviar_documento.html', {'form': form})

@login_required
def documentos_fila(request):
    #now = timezone.now()
    #cutoff_date = now - timezone.timedelta(days=5)
    #old_documents = DocumentoImpressao.objects.filter(data_envio__lt=cutoff_date)

    #for documento in old_documents:
        # Delete the file from the media folder
        #if documento.documento:
            #if os.path.isfile(documento.documento.path):
                #os.remove(documento.documento.path)
        # Delete the document from the database
        #documento.delete()

    documentos_nao_impressos = DocumentoImpressao.objects.filter(impresso=False).order_by('data_envio')
    cutoff_date = timezone.now() - timezone.timedelta(days=1)
    documentos_impressos = DocumentoImpressao.objects.filter(impresso=True, data_envio__gte=cutoff_date).order_by('-data_envio')

    # Paginação
    paginator = Paginator(documentos_impressos, 10)  # 10 documentos por página
    page = request.GET.get('page')
    try:
        documentos_impressos_paginados = paginator.page(page)
    except PageNotAnInteger:
        documentos_impressos_paginados = paginator.page(1)
    except EmptyPage:
        documentos_impressos_paginados = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'documentos_fila.html', {
        'documentos_nao_impressos': documentos_nao_impressos,
        'documentos_impressos': documentos_impressos_paginados
    })

@login_required
def visualizar_documento(request, pk):
    documento = get_object_or_404(DocumentoImpressao, pk=pk)
    return FileResponse(documento.documento.open(), content_type='application/pdf')

@login_required
def marcar_como_impresso(request, pk):
    documento = get_object_or_404(DocumentoImpressao, pk=pk)
    documento.impresso = True
    documento.usuario_impresso = request.user
    documento.save()
    return redirect('impressao:documentos_fila')


@user_passes_test(is_admin)
def consultar_impressoes(request):
    usuario = request.GET.get('usuario')
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    impressoes = DocumentoImpressao.objects.filter(impresso=True).order_by('-data_envio')

    if usuario:
        impressoes = impressoes.filter(usuario_impresso__id=usuario)
    if data_inicial:
        impressoes = impressoes.filter(data_envio__gte=data_inicial)
    if data_final:
        impressoes = impressoes.filter(data_envio__lte=data_final)

    paginator = Paginator(impressoes, 10)  # 10 impressões por página
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'consultar_impressoes.html', {
        'page_obj': page_obj,
        'usuarios': CustomUser.objects.all(),
    })