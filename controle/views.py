from django.template import loader
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime, timezone
from weasyprint import HTML
from .models import Motorista, Veiculo, TermoResponsabilidade, Setor, Multa
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
import base64
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q  # necessário para filtros complexos
from .utils import buscar_abastecimentos, buscar_abastecimentos_por_data, buscar_abastecimentos_recentes, acessar_abastecimento_externo, grupo_administrador
from django.utils.text import slugify
from itertools import chain
from django.contrib.auth.models import User 
from openpyxl import Workbook


@login_required
def home(request):
    return render(request, "controle/index.html")



# ----- TERMO VINCULA MOTORISTA/VEICULO ------
####### CRUD --> TERMO
@login_required
def criar_termo(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)

    if request.method == "POST":
        form = TermoResponsabilidadeForm(request.POST)
        assinatura_base64 = request.POST.get("assinatura_imagem")

        if not assinatura_base64:
            messages.error(request, "Assinatura não enviada. Por favor, assine antes de salvar.")
            return redirect("assinatura", pk=motorista.id)

        if form.is_valid():
            termo = form.save(commit=False)
            termo.motorista = motorista

            try:
                format, imgstr = assinatura_base64.split(';base64,')
                ext = format.split('/')[-1]
                nome_arquivo = f"assinatura_{slugify(motorista.nome)}.{ext}"
                termo.arquivo.save(nome_arquivo, ContentFile(base64.b64decode(imgstr)), save=False)
            except Exception as e:
                messages.error(request, f"Erro ao processar assinatura: {e}")
                return redirect("assinatura", pk=motorista.id)

            termo.save()

            if termo.veiculo:
                termo.veiculo.motoristas.add(motorista)

            messages.success(request, "Termo salvo com sucesso!")
            return redirect("listar_termos", pk=motorista.id)
    else:
        form = TermoResponsabilidadeForm(initial={'motorista': motorista})

    return render(request, "controle/assinatura.html", {"form": form, "motorista": motorista})

@login_required
def visualizar_termos(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    termos = TermoResponsabilidade.objects.filter(motorista=motorista)
    dicionario = {"termos" : termos,
                  "motorista" : motorista}
    return render(request, "controle/termos.html", dicionario)

@login_required
def lista_termo(request):
    # Listar todos os termos de responsabilidade
    termos = TermoResponsabilidade.objects.all() # LISTA TODOS SO TERMOS
    dicionario = {"termos" : termos}
    return render(request, "controle/termos.html", dicionario)

@login_required
def termo_responsabilidade(request, veiculo_id, motorista_id):
    motorista = Motorista.objects.get(id=motorista_id)
    veiculo = Veiculo.objects.get(id=veiculo_id)
    termo = TermoResponsabilidade.objects.filter(veiculo_id=veiculo_id, motorista_id=motorista_id).first()

    # Carrega o template
    template = loader.get_template("controle/termo_responsabilidade.html")

    #Carregar imagem da assinatura
    with termo.arquivo.open("rb") as f:
        assinatura_base64 = base64.b64encode(f.read()).decode("utf-8")
        
    img_data = f"data:image/png;base64,{assinatura_base64}"

    # Renderiza com o contexto
    html_string = template.render({
        'motorista': motorista,
        'veiculo': veiculo,
        'data_hoje': termo.data_assinatura.strftime("%d/%m/%Y"),
        'assinatura' : img_data 
    })

    # Gera o PDF com WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="termo_{motorista.nome}_{veiculo.placa}.pdf"'
    return response



# ----------------- MOTORISTA -----------------
####### CRUD --> MOTORISTA

# LISTAR
@login_required
def lista_motoristas(request):
    """
    Lista todos os motoristas cadastrados com:
    - Ordenação por nome (A-Z ou Z-A)
    - Filtro de pesquisa por nome, CPF ou CNH
    """
    
    # Obter todos os motoristas
    motoristas = Motorista.objects.all()

    # ----- Ordenação -----
    # Pega o parâmetro 'ordenar' da URL (?ordenar=a-z ou ?ordenar=z-a)
    ordem = request.GET.get("ordenar", "a-z")
    if ordem == "z-a":
        motoristas = motoristas.order_by("-nome")  # Z-A
    else:
        motoristas = motoristas.order_by("nome")   # A-Z padrão

    # ----- Filtro de pesquisa -----
    # Pega o parâmetro 'q' da URL (?q=texto)
    query = request.GET.get("q")
    if query:
        # Filtra motoristas cujo nome, CPF ou CNH contenha o texto digitado (case-insensitive)
        motoristas = motoristas.filter(
            Q(nome__icontains=query) | Q(cpf__icontains=query) | Q(cnh_numero__icontains=query)
        )

    # ----- Contexto -----
    dicionario = {
        "motoristas": motoristas,
        "ordenar": ordem,     # útil para manter o botão de filtro ativo no template
        "query": query or "", # mantém o termo digitado na barra de pesquisa
    }

    # Renderiza o template com os motoristas filtrados e ordenados
    return render(request, "controle/motorista.html", dicionario)

# CRIAR
@login_required
def criar_motorista(request):
    """
    Cria um novo motorista.
    - GET: mostra formulário vazio
    - POST: valida e salva
    """
    if request.method == "POST":
        form = MotoristaForm(request.POST, request.FILES)  # inclui arquivos
        if form.is_valid():
            form.save()
            return redirect("lista_motorista")  # depois de salvar, volta para a lista
    else:
        form = MotoristaForm()

    return render(request, "controle/motorista_form.html", {"form": form, "titulo": "Criar Condutor"})

# EDITAR
@login_required
def editar_motorista(request, pk):
    # busca o motorista ou retorna 404
    motorista = get_object_or_404(Motorista, pk=pk)

    if request.method == "POST":
        # se tiver campos de arquivo (ex: imagem da CNH) inclua request.FILES
        form = MotoristaForm(request.POST, request.FILES, instance=motorista)
        if form.is_valid():
            form.save()
            messages.success(request, "Motorista atualizado com sucesso.")
            # redireciona para a lista (ou para uma página de detalhe, se preferir)
            return redirect("lista_motorista")
        # se inválido, cai para o render abaixo com os erros disponíveis no form
    else:
        # GET -> exibe o form já preenchido com os dados do motorista
        form = MotoristaForm(instance=motorista)

    return render(
        request,
        "controle/motorista_form.html",
        {"form": form, "titulo": "Editar Motorista", "motorista": motorista},
    )

# EXCLUIR
@user_passes_test(grupo_administrador)
def excluir_motorista(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    if request.method == "POST":
        motorista.delete()
        return redirect("lista_motorista")
    return redirect("lista_motorista")  # fallback: se acessar GET, só volta



# ----------------- VEICULO -----------------
####### CRUD --> VEICULO

# LISTAR
@login_required
def listar_veiculo(request):
    # --------------------------
    # Base queryset
    # --------------------------
    if request.user.is_superuser:
        veiculos = Veiculo.objects.all()
    else:
        veiculos = Veiculo.objects.filter(created_by=request.user)

    # --------------------------
    # Filtro por placa
    # --------------------------
    query = request.GET.get("q")
    if query:
        veiculos = veiculos.filter(placa__icontains=query)

    # --------------------------
    # Filtro por setor
    # --------------------------
    setor_id = request.GET.get("setor")
    if setor_id:
        veiculos = veiculos.filter(setor_id=setor_id)

    # --------------------------
    # Filtro por status
    # --------------------------
    status = request.GET.get("status")
    if status:
        veiculos = veiculos.filter(status_atual=status)

    # --------------------------
    # Lista de setores e status para o template
    # --------------------------
    setores = Setor.objects.all()
    status_choices = Veiculo.STATUS_CHOICE.choices

    contexto = {
        "veiculo": veiculos,
        "query": query or "",
        "setores": setores,
        "setor_id": setor_id or "",
        "status_choices": status_choices,
        "status": status or "",
    }

    return render(request, "controle/veiculo.html", contexto)


# DETALHAR
@login_required
def detalhar_veiculo(request, pk):
    """
    Mostra todos os detalhes de um veículo específico
    e os últimos abastecimentos com status = 2.
    """
    veiculo = get_object_or_404(Veiculo, pk=pk)

    # Buscar últimos abastecimentos (últimos 30 dias)
    abastecimentos = buscar_abastecimentos(veiculo.placa, dias=30)

    contexto = {
        "veiculo": veiculo,
        "motoristas": veiculo.motoristas.all(),
        "abastecimentos": abastecimentos,
    }

    return render(request, "controle/detalhar_veiculo.html", contexto)

# CRIAR
@login_required
def criar_veiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST, request.FILES)
        if form.is_valid():
            veiculo = form.save(commit=False)  # não salva ainda
            veiculo.created_by = request.user   # associa ao usuário logado
            veiculo.save()                      # salva no banco
            return redirect('listar_veiculo')
    else:
        form = VeiculoForm()

    return render(
        request,
        'controle/veiculo_form.html',
        {'form': form, 'titulo': 'Criar Veículo'}
    )

# EDITAR 
@login_required
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)

    # --------------------------
    # Permissão: só quem criou ou admin pode editar
    # --------------------------
    if request.user != veiculo.created_by and not request.user.is_superuser:
        return HttpResponseForbidden("Você não tem permissão para editar este veículo.")

    # --------------------------
    # Processar formulário
    # --------------------------
    if request.method == 'POST':
        form = VeiculoForm(request.POST, request.FILES, instance=veiculo)
        if form.is_valid():
            veiculo = form.save(commit=False)  # evita sobrescrever created_by
            veiculo.save()
            form.save_m2m()  # necessário se houver campos ManyToMany
            return redirect('listar_veiculo')
    else:
        form = VeiculoForm(instance=veiculo)

    return render(
        request,
        'controle/veiculo_form.html',
        {'form': form, 'titulo': 'Editar Veículo'}
    )

# EXCLUIR
@login_required
def excluir_veiculo(request, pk):
    
    veiculo = get_object_or_404(Veiculo, pk=pk)

    # Permissão: só quem criou ou admin pode inativar
    if request.user != veiculo.created_by and not request.user.is_superuser:
        return HttpResponseForbidden("Você não tem permissão para excluir este veículo.")

    if request.method == 'POST':
        veiculo.status_atual = Veiculo.STATUS_CHOICE.INATIVO  # apenas muda o status
        veiculo.save()
        return redirect('listar_veiculo')

    return redirect('listar_veiculo')



# ------------ VISUALIZAR LOGS --------------

@user_passes_test(grupo_administrador, login_url='acesso_negado')
def logs_todos(request):
    logs_motorista = Motorista.history.all()
    logs_veiculo = Veiculo.history.all()
    logs_termo = TermoResponsabilidade.history.all()
    logs_multas = Multa.history.all()

    # Junta todos os logs
    todos_logs = sorted(
        chain(logs_motorista, logs_veiculo, logs_termo, logs_multas),
        key=lambda log: log.history_date or timezone.now(),
        reverse=True
    )

    logs_processados = []
    for log in todos_logs:
        # Pega o nome do modelo
        modelo = getattr(log.instance._meta, 'model_name', 'desconhecido') if hasattr(log, 'instance') and log.instance else 'desconhecido'

        # Pega o tipo de operação
        tipos = {
            '+': 'Criado',
            '~': 'Atualizado',
            '-': 'Deletado'
        }
        tipo_operacao = tipos.get(log.history_type, 'Desconhecido')

        # Descrição do objeto
        try:
            if modelo == 'motorista':
                descricao_objeto = getattr(log, 'nome', str(log))
            elif modelo == 'veiculo':
                descricao_objeto = getattr(log, 'placa', str(log))
            elif modelo == 'termoresponsabilidade':
                try:
                    veiculo = log.veiculo  # objeto Veiculo
                    motorista = log.motorista  # objeto Motorista
                    descricao_objeto = f"Termo - {veiculo} - {motorista}"
                except Exception:
                    descricao_objeto = "Termo - [dados indisponíveis]"

            else:
                descricao_objeto = str(log)
        except Exception:
            descricao_objeto = 'Erro ao processar descrição'

        logs_processados.append({
            'modelo': modelo.capitalize(),
            'descricao': descricao_objeto,
            'tipo_operacao': tipo_operacao,
            'usuario': getattr(log, 'history_user', None),
            'data': log.history_date,
            'motivo': getattr(log, 'history_change_reason', None),
        })

    return render(request, 'controle/logs_todos.html', {'logs': logs_processados})



# -------------- ABASTECIMENTO ---------------
#
@user_passes_test(grupo_administrador, login_url='acesso_negado')
def lista_abastecimentos(request):
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    if data_inicio and data_fim:
        # Se o usuário colocou datas, busca pelo intervalo
        abastecimentos = buscar_abastecimentos_por_data(
            data_inicio=data_inicio,
            data_fim=data_fim
        )
    else:
        # Caso contrário, pega os abastecimentos de hoje
        abastecimentos = buscar_abastecimentos_recentes()

    return render(request, "controle/abastecimento.html", {
        "abastecimentos": abastecimentos,
        "data_inicio": data_inicio or "",
        "data_fim": data_fim or "",
    })

@user_passes_test(grupo_administrador, login_url='acesso_negado')
def acessar_abastecimento(request, cod_abastecimento):

    # Chama a função do utils.py que faz login e retorna o HTML da página externa
    html = acessar_abastecimento_externo(cod_abastecimento)

    if not html:
        return HttpResponse("Falha no login no site externo.", status=403)

    # Retorna o HTML da página externa diretamente no navegador
    return redirect(html)



# ----------------- Usuarios -----------------
####### CRUD --> USUARIOS
@user_passes_test(grupo_administrador, login_url='acesso_negado')
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "controle/listar_usuarios.html", {"usuarios": usuarios})

@user_passes_test(grupo_administrador, login_url='acesso_negado')
def criar_usuario(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário criado com sucesso!")
            return redirect("lista_usuarios")
    else:
        form = UserForm()
    return render(request, "controle/usuarios_form.html", {"form": form, "titulo": "Criar Usuário"})

@user_passes_test(grupo_administrador, login_url='acesso_negado')
def editar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            return redirect("lista_usuarios")
    else:
        form = UserForm(instance=user)
    return render(request, "controle/usuarios_form.html", {"form": form, "titulo": "Editar Usuário"})

@user_passes_test(grupo_administrador, login_url='acesso_negado')
def deletar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Usuário deletado com sucesso!")
        return redirect("lista_usuarios")
    return render(request, "usuarios/confirm_delete.html", {"usuario": user})

def acesso_negado(request):
    return render(request, 'controle/acesso_negado.html', status=403)

#-------------- MULTAS -------------
@login_required
def criar_multa(request):
    if request.method == 'POST':
        form = MultaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_multas')
    else:
        form = MultaForm()
    return render(request, 'controle/multa_form.html', {'form': form})

@login_required
def atualizar_status_multa(request, pk):
    multa = get_object_or_404(Multa, pk=pk)

    if request.method == "POST":
        form = AtualizarStatusMultaForm(request.POST, request.FILES, instance=multa)
        if form.is_valid():
            form.save()
            messages.success(request, "Status da multa atualizado com sucesso.")
            return redirect("listar_multas")
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = AtualizarStatusMultaForm(instance=multa)

    return render(request, "controle/multa_editar.html", {"form": form, "multa": multa})

@login_required
def criar_memorando(request, multa_id):
    # Busca a multa
    multa = get_object_or_404(Multa, pk=multa_id)

    # Renderiza o template HTML do memorando
    html_string = render_to_string("controle/memorando.html", {
        "multa": multa,
    })

    # Gera o PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # Retorna como resposta no navegador
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename=memorando_{multa.id}.pdf'
    return response

@login_required
def listar_multas(request):
    multas = Multa.objects.all().order_by('-data_hora_infracao')

    status_multa = request.GET.get('status_multa')
    status_pagamento = request.GET.get('status_pagamento')
    setor = request.GET.get('setor')

    if status_multa and status_multa != "todos":
        multas = multas.filter(status_multa=status_multa)

    if status_pagamento and status_pagamento != "todos":
        multas = multas.filter(status_pagamento=status_pagamento)

    if setor and setor != "todos":
        multas = multas.filter(setor=setor)

    context = {
        'multas': multas,
        'status_multa_selecionado': status_multa,
        'status_pagamento_selecionado': status_pagamento,
        'setor_selecionado': setor,
        'setores': Multa.objects.values_list('setor', flat=True).distinct(),
    }
    return render(request, 'controle/listar_multas.html', context)

@login_required
def pagar_multa(request, pk):
    multa = get_object_or_404(Multa, pk=pk)

    if request.method == "POST":
        form = PagamentoMultaForm(request.POST, request.FILES, instance=multa)
        if form.is_valid():
            form.save()
            messages.success(request, "Pagamento registrado com sucesso.")
            return redirect("listar_multas")
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = PagamentoMultaForm(instance=multa)

    return render(request, "controle/pagar_multa.html", {"form": form, "multa": multa})

@login_required
def detalhar_multa(request, pk):
    multa = get_object_or_404(Multa, pk=pk)
    return render(request, "controle/detalhar_multa.html", {"multa": multa})

def trocar_setor(request, pk):
    multa = get_object_or_404(Multa, id=pk)
    setores = Setor.objects.all()  # 🔁 lista de setores com nome e descrição

    if request.method == 'POST':
        form = TrocaSetorForm(request.POST, instance=multa)
        if form.is_valid():
            form.save()
            return redirect('listar_multas')
    else:
        form = TrocaSetorForm(instance=multa)

    return render(request, 'controle/setor_multa.html', {
        'form': form,
        'multa': multa,
        'setores': setores  # 🔁 envia para o JS preencher a descrição
    })
# Relatorios



from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.hyperlink import Hyperlink
from django.conf import settings
from .models import Multa

@user_passes_test(grupo_administrador, login_url='acesso_negado')
def exportar_multas_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Multas"

    # Cabeçalhos
    ws.append([
        'ID', 'Placa', 'Setor', 'Setor Descrição', 'Motorista',
        'Infração', 'Valor', 'Gravidade',
        'Data/Hora Infração', 'Local', 'Órgão Autuador',
        'Status Multa', 'Status Pagamento', 'Prazo Pagamento', 'Data Registro',
        'Documento Recebido', 'Comprovante Pagamento', 'Notificação Infração'
    ])

    # Estilo para links
    link_font = Font(color="0000FF", underline="single")

    multas = Multa.objects.select_related('veiculo', 'motorista', 'infracao')

    for multa in multas:
        row = [
            multa.id,
            multa.veiculo.placa if multa.veiculo else '',
            multa.setor or '',
            multa.setor_descricao or '',
            multa.motorista.nome if multa.motorista else '',
            multa.infracao.descricao if multa.infracao else '',
            multa.valor if multa.infracao else '',
            multa.gravidade if multa.infracao else '',
            multa.data_hora_infracao.strftime('%d/%m/%Y %H:%M'),
            multa.local,
            multa.orgao_autuador,
            multa.get_status_multa_display(),
            multa.get_status_pagamento_display(),
            multa.prazo_pagamento.strftime('%d/%m/%Y'),
            multa.data_registro.strftime('%d/%m/%Y %H:%M'),
            '', '', ''  # Reservando espaços para links
        ]
        ws.append(row)

        # Index da linha atual
        current_row = ws.max_row

        # Construir URLs completas
        domain = request.build_absolute_uri('/')[:-1]  # Remove a barra final
        links = [
            multa.documento_recebido.url if multa.documento_recebido else '',
            multa.comprovante_pagamento.url if multa.comprovante_pagamento else '',
            multa.notificacao_infracao.url if multa.notificacao_infracao else '',
        ]

        for i, file_url in enumerate(links):
            if file_url:
                cell = ws.cell(row=current_row, column=16 + i)
                full_url = f"{domain}{file_url}"
                cell.value = "📎 Abrir Documento"
                cell.hyperlink = full_url
                cell.font = link_font

    # Retorna como arquivo para download
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=multas.xlsx'
    wb.save(response)
    return response

@user_passes_test(grupo_administrador, login_url='acesso_negado')
def listar_relatorios(request):
    return render(request, 'controle/listar_relatorios.html')   