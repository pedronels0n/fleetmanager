from django.template import loader
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime
from weasyprint import HTML
from .models import Motorista, Veiculo, TermoResponsabilidade, Setor
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from .forms import MotoristaForm, TermoResponsabilidadeForm, VeiculoForm
import base64
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # necessário para filtros complexos
from .utils import buscar_abastecimentos, buscar_abastecimentos_por_data, buscar_abastecimentos_recentes, acessar_abastecimento_externo
from django.utils.text import slugify
from itertools import chain
import os

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
@login_required
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

@login_required
def logs_todos(request):
    logs_motorista = Motorista.history.all()
    logs_veiculo = Veiculo.history.all()
    logs_termo = TermoResponsabilidade.history.all()

    # Junta todos os logs
    todos_logs = sorted(
        chain(logs_motorista, logs_veiculo, logs_termo),
        key=lambda log: log.history_date,
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


def acessar_abastecimento(request, cod_abastecimento):

    # Chama a função do utils.py que faz login e retorna o HTML da página externa
    html = acessar_abastecimento_externo(cod_abastecimento)

    if not html:
        return HttpResponse("Falha no login no site externo.", status=403)

    # Retorna o HTML da página externa diretamente no navegador
    return redirect(html)



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserForm
from django.contrib import messages

def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "controle/listar_usuarios.html", {"usuarios": usuarios})

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

def deletar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Usuário deletado com sucesso!")
        return redirect("lista_usuarios")
    return render(request, "usuarios/confirm_delete.html", {"usuario": user})
