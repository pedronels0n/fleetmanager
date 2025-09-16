from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("assinatura/<int:pk>/", views.criar_termo, name="assinatura"),
    path('listar_termo/', views.lista_termo, name='termos'),
    path('termo/<int:veiculo_id>/<int:motorista_id>/', views.termo_responsabilidade, name='termo_responsabilidade'),
    #LINKS PARA CRUD  --- CONDUTOR
    path("condutor/", views.lista_motoristas, name="lista_motorista"),
    path("condutor/novo/", views.criar_motorista, name="criar_motorista"),
    path("condutor/<int:pk>/editar/", views.editar_motorista, name="editar_motorista"),
    path("condutor/<int:pk>/excluir/", views.excluir_motorista, name="excluir_motorista"),
    path("condutor/<int:pk>/listar_termo/", views.visualizar_termos, name="listar_termos"),
    #LINKS PARA CRUD --- VEIUCLO
    path("veiculo/", views.listar_veiculo, name="listar_veiculo"),
    path("veiculo/<int:pk>/detalhar/", views.detalhar_veiculo, name="detalhar_veiculo"),
    path("veiculo/criar", views.criar_veiculo, name='criar_veiculo'),  # criar novo veículo
    path("veiculo/<int:pk>/editar", views.editar_veiculo, name='editar_veiculo'),  # editar veículo existente
    path('veiculo/<int:pk>/excluir', views.excluir_veiculo, name='excluir_veiculo'),
    #Links para LOGIN/LOGOUT
    path("login/", auth_views.LoginView.as_view(template_name="controle/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path('logs/', views.logs_todos, name='logs_todos'),
]