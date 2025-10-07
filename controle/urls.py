from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ==========================
    # PÁGINA INICIAL
    # ==========================
    path("", views.home, name="home"),

    # ==========================
    # TERMOS DE RESPONSABILIDADE
    # ==========================
    path("assinatura/<int:pk>/", views.criar_termo, name="assinatura"),
    path("listar_termo/", views.lista_termo, name="termos"),
    path("termo/<int:veiculo_id>/<int:motorista_id>/", views.termo_responsabilidade, name="termo_responsabilidade"),

    # ==========================
    # CONDUTORES (CRUD)
    # ==========================
    path("condutor/", views.lista_motoristas, name="lista_motorista"),
    path("condutor/novo/", views.criar_motorista, name="criar_motorista"),
    path("condutor/<int:pk>/editar/", views.editar_motorista, name="editar_motorista"),
    path("condutor/<int:pk>/excluir/", views.excluir_motorista, name="excluir_motorista"),
    path("condutor/<int:pk>/listar_termo/", views.visualizar_termos, name="listar_termos"),

    # ==========================
    # VEÍCULOS (CRUD)
    # ==========================
    path("veiculo/", views.listar_veiculo, name="listar_veiculo"),
    path("veiculo/criar/", views.criar_veiculo, name="criar_veiculo"),
    path("veiculo/<int:pk>/detalhar/", views.detalhar_veiculo, name="detalhar_veiculo"),
    path("veiculo/<int:pk>/editar/", views.editar_veiculo, name="editar_veiculo"),
    path("veiculo/<int:pk>/excluir/", views.excluir_veiculo, name="excluir_veiculo"),

    # ==========================
    # AUTENTICAÇÃO
    # ==========================
    path("login/", auth_views.LoginView.as_view(template_name="controle/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("acesso-negado/", views.acesso_negado, name="acesso_negado"),

    # ==========================
    # LOGS DO SISTEMA
    # ==========================
    path("logs/", views.logs_todos, name="logs_todos"),

    # ==========================
    # ABASTECIMENTOS
    # ==========================
    path("abastecimentos/", views.lista_abastecimentos, name="abastecimentos"),
    path("abastecimento/criar/", views.registrar_abastecimento, name="criar_abastecimento"),
    path("abastecimento/<int:pk>/editar/", views.editar_abastecimento, name="editar_abastecimento"),
    path("abastecimento/<int:pk>/excluir/", views.excluir_abastecimento, name="excluir_abastecimento"),

    # ==========================
    # USUÁRIOS (CRUD)
    # ==========================
    path("usuarios/", views.lista_usuarios, name="lista_usuarios"),
    path("usuarios/novo/", views.criar_usuario, name="criar_usuario"),
    path("usuarios/<int:pk>/editar/", views.editar_usuario, name="editar_usuario"),
    path("usuarios/<int:pk>/excluir/", views.deletar_usuario, name="excluir_usuario"),

    # ==========================
    # MULTAS (CRUD + AÇÕES)
    # ==========================
    path("multas/listar/", views.listar_multas, name="listar_multas"),
    path("multas/criar/", views.criar_multa, name="criar_multa"),
    path("multas/<int:multa_id>/memorando/", views.criar_memorando, name="criar_memorando"),
    path("multa/<int:pk>/editar/", views.atualizar_status_multa, name="editar_multa"),
    path("multas/<int:pk>/pagar/", views.pagar_multa, name="pagar_multa"),
    path("multas/<int:pk>/detalhar/", views.detalhar_multa, name="detalhar_multa"),
    path("multas/<int:pk>/trocar-setor/", views.trocar_setor, name="trocar_setor"),

    # ==========================
    # RELATÓRIOS
    # ==========================
    path("relatorios/", views.listar_relatorios, name="listar_relatorios"),
    path("exportar-multas-excel/", views.exportar_multas_excel, name="exportar_multas_excel"),

    # ==========================
    # CONTAS A PAGAR
    # ==========================
    path("conta/criar/", views.criar_conta_pagamento, name="criar_conta_pagamento"),
]
