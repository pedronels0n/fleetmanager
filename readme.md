# 🚗 Sistema de Gestão de Frotas - Prefeitura de Lauro de Freitas/BA

## 🎯 Objetivo do Sistema
Desenvolver um sistema web para a **gestão eficiente da frota de veículos** da Prefeitura de Lauro de Freitas, permitindo:
- Controle de veículos e motoristas
- Registro e acompanhamento de multas
- Solicitação e liberação de pedágios
- Emissão de documentos oficiais em PDF
- Geração de relatórios e consultas detalhadas

---

## 🌐 Acesso ao Sistema
🔗 **Ambiente de Teste:** [https://gestorfleet.com/controle/](https://gestorfleet.com/controle/)

---

## 🧩 Módulos Principais

### 🚘 Cadastro de Veículos
- Inclusão de dados essenciais (placa, RENAVAM, marca, modelo, ano, combustível, categoria, chassi, etc.)
- Upload de documentos (CRLV, licenciamento, seguro, etc.)
- Histórico de vinculação com motoristas

### 👨‍✈️ Cadastro de Motoristas
- Dados pessoais (nome, CPF, RG, CNH, validade, categoria, etc.)
- Upload de documentos pessoais e CNH
- Histórico de veículos conduzidos

### 🔗 Vinculação Motorista-Veículo
- Atribuição de veículo(s) ao motorista
- Emissão de **termo de responsabilidade (PDF)**
- Registro de data/hora da vinculação

### 🚨 Gestão de Multas
- Registro de multas por veículo
- Dados da infração (data, local, órgão autuador, valor, pontos, natureza)
- Upload de documento da multa
- Emissão de **notificação em PDF** para o motorista

### 🛣️ Gestão de Pedágio *(em desenvolvimento)*
- Cadastro de veículos para passagem em pedágio
- Formulário de solicitação de liberação
- Emissão de **pedido formal em PDF**
- Histórico de liberações e solicitações

### 📑 Emissão de Documentos
- Termo de responsabilidade motorista-veículo
- Notificação de multa
- Pedido de liberação de pedágio

### 📊 Relatórios e Consultas *(em desenvolvimento)*
- Relatórios por veículo, motorista ou tipo de infração
- Filtros por datas, categorias e status
- Exportação para **PDF ou Excel**

---

## ⚙️ Modos de Operação

### 🧑‍💼 Administrativo (Administração da Frota)
- Acesso completo a todos os módulos
- Cadastro, edição e desativação de motoristas e veículos
- Emissão de documentos e relatórios
- Gerenciamento de permissões de usuários

### 🧑‍💻 Operacional (Secretarias/Setores Solicitantes)
- Solicitação de liberação de pedágio
- Visualização de veículos e motoristas vinculados
- Download de documentos já gerados

### 📋 Visualização (Auditoria/Controladoria)
- Acesso restrito a relatórios e PDFs emitidos
- Sem permissões de edição
- Consultas por filtros e histórico

---

## 🗄️ Modelo de Dados (Simplificado)
- **Veiculos**
- **Motoristas**
- **Vinculos** (Motorista ↔ Veículo)
- **Multas**
- **Documentos**
- **Pedagios**
- **Usuarios**
- **Termos** (PDFs gerados)

---

## 📌 Funcionalidades Técnicas
- Interface web responsiva
- Autenticação e permissões por perfil de usuário
- Upload e download de arquivos (PDF, imagens, DOC)
- Geração automatizada de PDFs
- Backup automático dos dados
- Auditoria de ações (quem fez o quê e quando)

---

## 🛠️ Tecnologias Utilizadas
- **Backend:** Django (Python)
- **Banco de Dados:** PostgreSQL
- **Servidor de Aplicação:** Gunicorn
- **Servidor Web:** Nginx
- **Frontend:** HTML5, CSS3, JavaScript (Bootstrap/React opcional)
- **Relatórios/PDFs:** ReportLab / WeasyPrint
- **Controle de Versão:** Git + GitHub

---

## 🔒 Segurança
- **Fail2Ban** configurado para proteção contra ataques de força bruta
- **HTTPS** habilitado com **Certbot (Let's Encrypt)**
- **Controle de permissões** por perfil de usuário
- **Auditoria de ações** para rastreabilidade

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10+
- Django 4.x
- PostgreSQL
- Git

### Passos
```bash
# Clone o repositório
git clone https://github.com/pedronels0n/fleetmanager

# Acesse a pasta do projeto
cd sistema-gestao-frotas

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Inicie o servidor de desenvolvimento
python manage.py runserver
