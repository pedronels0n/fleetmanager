# 🚗 Sistema de Gestão de Frotas - Gestão Publica

## 🎯 Objetivo do Sistema

O Sistema de Gestão de Frotas foi desenvolvido para proporcionar **controle total e eficiente dos veículos oficiais** da Prefeitura. Ele permite o gerenciamento centralizado de veículos, motoristas, multas, abastecimentos, manutenções, documentos e auditoria, garantindo segurança, rastreabilidade e praticidade para os gestores públicos.

---

## 🧩 Módulos e Funcionalidades

### 1. Cadastro de Veículos

- Registro completo: placa, RENAVAM, chassi, marca, modelo, ano, cor, tipo de frota (próprio/locado), tipo de combustível, tipo de modelo (hatch, sedan, SUV, etc.).
- Upload de documentos obrigatórios: CRLV, seguro.
- Classificação por setor/departamento (Secretarias).
- Histórico de motoristas vinculados (muitos para muitos).
- Controle de status: ativo, inativo, manutenção, vendido.
- Auditoria automática de criação e modificações (via `django-simple-history`).

### 2. Cadastro de Motoristas

- Dados pessoais: nome, CPF, RG, telefone, data de nascimento.
- CNH: número, validade, categoria (A, B, C, D, E, etc.).
- Upload da CNH digitalizada.
- Status: ativo ou inativo.
- Relacionamento com veículos (muitos para muitos).

### 3. Vinculação Veículo ↔ Motorista

- Associação dinâmica de motoristas a veículos.
- Geração automática de Termo de Responsabilidade em PDF.
- Registro de histórico de vínculos.

### 4. Gestão de Multas

- Registro detalhado de infrações: placa, local, órgão autuador, valor, pontos, tipo de infração.
- Relacionamento com motorista (opcional).
- Upload de documentos: auto de infração, notificação, comprovante, memorando.
- Status da multa: enviado/recebido.
- Status de pagamento: pendente/pago.
- Integração com tipos de infrações (`InfracaoTransito`).
- Validações automáticas: impede salvar multa como recebida/paga sem documentos.
- Associação de conta de pagamento para cada multa.

### 5. Abastecimentos

- Registro de abastecimentos por veículo.
- Quilometragem, litros, valor total, valor por litro (calculado automaticamente).
- Motorista responsável, posto, observações.
- Histórico de abastecimentos e cálculo de média km/litro.
- Atualização automática do hodômetro do veículo.

### 6. Manutenção de Veículos (em desenvolvimento)

- Registro de revisões/manutenções realizadas.
- Quilometragem, tipo de manutenção, data, observações.

### 7. Emissão de Documentos

- Termo de responsabilidade (motorista ↔ veículo).
- Notificação de multa.
- Memorando da multa.
- Todos os documentos gerados e armazenados em PDF.

### 8. Auditoria e Histórico

- Histórico de alterações para todos os registros principais (motorista, veículo, multa, termo).
- Rastreabilidade de quem criou/modificou (usuário responsável).

### 9. Relatórios

- Exportação de multas para Excel (.xlsx).
- Visualização de dados e estatísticas da frota.

### 10. Usuários e Permissões

- Cadastro e gerenciamento de usuários.
- Controle de permissões por perfil.
- Auditoria de ações.

---

## 🗄️ Modelo de Dados (Principais Tabelas)

- **Veiculo**
- **Motorista**
- **Multa**
- **Abastecimento**
- **TermoResponsabilidade**
- **InfracaoTransito**
- **ContaPagamento**
- **Setor**
- **Usuário (Django)**

---

## 📌 Funcionalidades Técnicas

- Interface web responsiva (Bootstrap).
- Autenticação e permissões por perfil de usuário.
- Upload e download de arquivos (PDF, imagens).
- Geração automatizada de PDFs (WeasyPrint).
- Exportação de dados para Excel (openpyxl).
- Backup automático dos dados.
- Auditoria de ações (django-simple-history).
- Filtros avançados e busca em todos os módulos.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django (Python)
- **Banco de Dados:** PostgreSQL
- **Servidor de Aplicação:** Gunicorn
- **Servidor Web:** Nginx
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
- **Relatórios/PDFs:** WeasyPrint, openpyxl
- **Controle de Versão:** Git + GitHub

---

## 🔒 Segurança

- **Fail2Ban** para proteção contra ataques de força bruta.
- **HTTPS** habilitado com Certbot (Let's Encrypt).
- **Controle de permissões** por perfil de usuário.
- **Auditoria de ações** para rastreabilidade.

---

## 🌐 Acesso ao Sistema

- **Ambiente de Teste:** [https://gestorfleet.com/controle/](https://gestorfleet.com/controle/)
- **Usuário:** testegit
- **Senha:** testegit

---

## 📦 Instalação e Execução

### Pré-requisitos

- Python 3.10+
- Django 5.x
- PostgreSQL
- Git

### Instalação

1. Clone o repositório:
    ```bash
    git clone 
    cd gestorfleet
    ```

2. Crie e ative o ambiente virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure o banco de dados PostgreSQL e as variáveis de ambiente (`.env`).

5. Execute as migrações:
    ```bash
    python manage.py migrate
    ```

6. Crie um superusuário:
    ```bash
    python manage.py createsuperuser
    ```

7. Inicie o servidor:
    ```bash
    python manage.py runserver
    ```

---

## 📚 Documentação

- O código está documentado nos arquivos de models, views e forms.
- Para dúvidas sobre endpoints, consulte o arquivo `urls.py` ou acesse `/admin/` para visualizar os modelos.

---

## 🤝 Contribuição

Contribuições são bem-vindas!  
Abra uma issue ou envie um pull request com sugestões, correções ou novas funcionalidades.

---

## 📝 Licença

Este projeto é mantido pela SegenCode.  
É disponibilizado para uso livre, podendo ser usado, modificado e distribuído livremente, inclusive para fins comerciais.  

No entanto, a atribuição à SegenCode é apreciada.  

---


