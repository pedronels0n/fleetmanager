from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from django.conf import settings
from django.core.exceptions import ValidationError

class Setor(models.Model):
    # Nome do setor/departamento, único para evitar duplicidade
    nome = models.CharField(
        max_length=100,  # Limite de 100 caracteres
        unique=True      # Garante que não existam dois setores com o mesmo nome
    )
    
    # Descrição opcional do setor, pode conter informações adicionais
    descricao = models.TextField(
        blank=True,  # Permite que o campo fique vazio no formulário/admin
        null=True    # Permite que o campo seja nulo no banco de dados
    )

    def __str__(self):
        """
        Representação do objeto como string.
        Útil para exibir o setor no admin, listas ou logs.
        """
        return self.nome

class Veiculo(models.Model):
    # -----------------------------
    # DADOS ESSENCIAIS DO VEÍCULO
    # -----------------------------
    placa = models.CharField(max_length=10, unique=True)   # Placa única
    renavam = models.CharField(max_length=20, unique=True) # RENAVAM único
    marca = models.CharField(max_length=50)               # Marca do veículo
    modelo = models.CharField(max_length=50)             # Nome do modelo
    ano = models.PositiveIntegerField()                  # Ano de fabricação
    ano_modelo = models.PositiveIntegerField()           # Ano do Modelo    
    chassi = models.CharField(max_length=50, unique=True) # Número do chassi
    
    # -----------------------------
    # TIPOS DE FROTA
    # Usamos TextChoices para ter autocomplete no código e rótulos legíveis
    # -----------------------------
    class TiposdeFrota(models.TextChoices):
        PROPIO = 'PROPRIO', 'PROPRIO'
        LOCADO = 'LOCADO', 'LOCADO'

    tipo_frota = models.CharField(
    max_length=30,
    choices=TiposdeFrota.choices,
    default=TiposdeFrota.PROPIO,
)
    # -----------------------------
    # TIPOS DE CORES
    # Usamos TextChoices para ter autocomplete no código e rótulos legíveis
    # -----------------------------

    class Cores(models.TextChoices):
        BRANCO = 'BRANCO', 'Branco'
        PRATA = 'PRATA', 'Prata'
        AZUL = 'AZUL', 'Azul'
        CINZA = 'CINZA', 'Cinza'
        VERMELHO = 'VERMELHO', 'Vermelho'
        PRETO = 'PRETO', 'Preto'
        AMARELO = 'AMARELO', 'Amarelo'

    cor = models.CharField(max_length=30, choices=Cores.choices, default=Cores.BRANCO)


    # -----------------------------
    # TIPOS DE MODELO (Hatch, Sedan, SUV, etc.)
    # Usamos TextChoices para ter autocomplete no código e rótulos legíveis
    # -----------------------------
    class TipoModelo(models.TextChoices):
        HATCH = 'HATCH', 'Hatch'
        SEDAN = 'SEDAN', 'Sedã'
        SUV = 'SUV', 'SUV'
        CROSSOVER = 'CROSSOVER', 'Crossover'
        COUPE = 'COUPE', 'Coupé'
        CONVERSIVEL = 'CONVERSIVEL', 'Conversível'
        PERUA = 'PERUA', 'Perua / Station Wagon'
        PICKUP = 'PICKUP', 'Pick-up / Caminhonete'
        MINIVAN = 'MINIVAN', 'Minivan'
        VAN = 'VAN', 'Van de Carga ou Passageiros'
        FURGAO = 'FURGAO', 'Furgão'
        UTILITARIO = 'UTILITARIO', 'Utilitário Leve'
        CAMINHAO = 'CAMINHAO', 'Caminhão'
        ONIBUS = 'ONIBUS', 'Ônibus / Micro-ônibus'
        OFFROAD = 'OFFROAD', 'Off-road / 4x4'
        BUGGY = 'BUGGY', 'Buggy'
        MOTO = 'MOTO', 'Moto'


    tipo_modelo = models.CharField(
        max_length=30,                   # tamanho máximo do texto salvo no banco
        choices=TipoModelo.choices,     # define as opções disponíveis
        default=TipoModelo.HATCH        # valor padrão se nenhum for escolhido
    )

    # -----------------------------
    # TIPOS DE COMBUSTÍVEL
    # TextChoices para facilitar o uso no código
    # -----------------------------
    class TipoCombustivel(models.TextChoices):
        GASOLINA = 'G', 'Gasolina'
        ALCOOL = 'A', 'Álcool'
        DIESEL = 'D', 'Diesel'
        ELETRICO = 'E', 'Elétrico'
        HIBRIDO = 'H', 'Híbrido'
        FLEX = 'F', 'Flex'
    tipo_combustivel = models.CharField(
        max_length=1,                     # salva apenas uma letra no banco
        choices=TipoCombustivel.choices,  # opções disponíveis
        default=TipoCombustivel.FLEX  # valor padrão
    )

    # -----------------------------
    # UPLOAD DE DOCUMENTOS
    # É necessário configurar MEDIA_ROOT e MEDIA_URL no settings.py
    # -----------------------------
    crlv = models.FileField(
        upload_to='documentos/veiculos/crlv/', # pasta onde será salvo
        blank=True,                            # permite campo vazio
        null=True
    )
    seguro = models.FileField(
        upload_to='documentos/veiculos/seguro/',
        blank=True,
        null=True
    )

    # -----------------------------
    # HISTÓRICO DE MOTORISTAS
    # Vários motoristas podem estar vinculados ao mesmo veículo
    # -----------------------------
    motoristas = models.ManyToManyField(
        'Motorista',           # faz referência ao modelo Motorista
        blank=True,            # permite que o veículo não tenha motorista vinculado
        related_name='veiculos' # permite acessar veiculos de um motorista
    )

    # -----------------------------
    # CONTROLE DE CRIAÇÃO/ATUALIZAÇÃO
    # -----------------------------
    created_at = models.DateTimeField(auto_now_add=True)  # salva a data de criação
    updated_at = models.DateTimeField(auto_now=True)      # salva a data da última atualização

    #Status atual do veículo
    class STATUS_CHOICE(models.TextChoices):
        ATIVO = 'AT', 'Ativo'
        INATIVO = 'IN', 'Inativo'
        MANUTENCAO = 'MA', 'Em manutenção'
        VENDIDO = 'VE', 'Vendido'
    
    status_atual = models.CharField(
        max_length=2,
        choices=STATUS_CHOICE.choices,
        default=STATUS_CHOICE.ATIVO
    )

    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='veiculos', null=True)
    history = HistoricalRecords()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True,               # permite ficar vazio
                                   blank=True,
                                   on_delete=models.SET_NULL
    )



    def __str__(self):
        """
        Representação do objeto como string.
        Útil para exibir no admin e em listas.
        """
        return f"{self.placa} - {self.marca} {self.modelo}"
    
class Motorista(models.Model):
    # Dados pessoais
    nome = models.CharField(max_length=100)                        # Nome completo
    cpf = models.CharField(max_length=14, unique=True)             # CPF (único)
    rg = models.CharField(max_length=20, blank=True, null=True)    # RG (opcional)
    telefone = models.CharField(max_length=16) # Telefone
    data_nacimento = models.DateField(default=timezone.now)
    # status
    class STATUS_MOTORISTA_CHOICE(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        INATIVO = 'INATIVO', 'Inativo'
    
    status_atual = models.CharField(
        max_length=7,
        choices=STATUS_MOTORISTA_CHOICE.choices,
        default=STATUS_MOTORISTA_CHOICE.ATIVO, )
    

    # Dados da CNH
    cnh_numero = models.CharField(max_length=20, unique=True)      # Número da CNH
    cnh_validade = models.DateField(default=timezone.now)                              # Data de validade da CNH
    
    class CNH_CHOICE(models.TextChoices):
        A = 'A', 'A - Moto'
        B = 'B', 'B - Carro'
        C = 'C', 'C - Caminhão'
        D = 'D', 'D - Ônibus'
        E = 'E', 'E - Carreta'
        AB = 'AB', 'AB - Moto e Carro'
        AD = 'AD', 'AD - Caminhão e Carro'
        AE = 'AE', 'AE - Caminhão com reboque e Carro'

    cnh_categoria = models.CharField(max_length=2,  # Tanho da STRING
                                choices=CNH_CHOICE.choices, # Listando o conteudo da class CNH_CHOICE 
                                default=CNH_CHOICE.B) # Valor padrao B CARRO
    

    # Upload do documento da CNH
    cnh_arquivo = models.FileField(
        upload_to='documentos/motoristas/cnh/', # Pasta onde o arquvio sera salvo
        blank=True,                             # Permite nao enviar o arquivo
        null=True                               # Permite Campo Vazio no Banco
    )

    history = HistoricalRecords()

    def __str__(self):
        """
        Representação do objeto como string.
        Útil para exibir no admin e em listas.
        """
        return f"{self.nome}"
    
class ManutencaoVeiculo(models.Model):
    veiculo = models.ForeignKey('Veiculo', on_delete=models.CASCADE, related_name='manutencoes')
    
    # Quilometragem na revisão
    km = models.PositiveIntegerField(help_text="Quilometragem do veículo no momento da revisão")
    
    # Tipo de manutenção (opcional)
    tipo_manutencao = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Ex: Troca de óleo, Freios, Pneus, Revisão geral"
    )
    
    # Data da manutenção
    data = models.DateField(default=timezone.now)
    
    # Observações adicionais
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.veiculo.placa} - {self.tipo_manutencao or 'Manutenção'} em {self.data}"
    
from django.db import models
from django.utils import timezone

class Multa(models.Model):

    numero_memorando = models.PositiveIntegerField(blank=True, null=True,)

    auto_infracao = models.CharField(blank=True, null=True)

    veiculo = models.ForeignKey(
        'Veiculo',
        on_delete=models.CASCADE,
        related_name='multas'
    )

    # 🔑 Setor congelado no momento do registro
    setor = models.CharField(
        max_length=100,
        help_text="Setor do veículo no momento da infração",
        null=True,
        blank=True,
    )
    setor_descricao = models.CharField(max_length=255, blank=True)

    motorista = models.ForeignKey(
        'Motorista',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='multas'
    )

    infracao = models.ForeignKey(
    'InfracaoTransito',
    on_delete=models.PROTECT,
    related_name='multas',
    help_text="Tipo de infração cometida",
    null=True,   # permite nulo
    blank=True   # permite vazio em formulários
    )

    data_hora_infracao = models.DateTimeField(default=timezone.now)
    local = models.CharField(max_length=200)
    orgao_autuador = models.CharField(max_length=100)
    prazo_pagamento = models.DateField(default=timezone.now)

    STATUS_MULTA_CHOICES = [
        ('enviado', 'Enviado'),
        ('recebido', 'Recebido'),
    ]
    STATUS_PAGAMENTO_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
    ]

    status_multa = models.CharField(
        max_length=20,
        choices=STATUS_MULTA_CHOICES,
        default='enviado'
    )
    status_pagamento = models.CharField(
        max_length=20,
        choices=STATUS_PAGAMENTO_CHOICES,
        default='pendente'
    )

    documento_recebido = models.FileField(
        upload_to='documentos/multas/recebidos/',
        blank=True,
        null=True,
        help_text="Documento com carimbo de recebido"
    )
    comprovante_pagamento = models.FileField(
        upload_to='documentos/multas/comprovantes/',
        blank=True,
        null=True,
        help_text="Comprovante de pagamento"
    )

    notificacao_infracao = models.FileField(
        upload_to='documentos/multas/',
        blank=True,
        null=True,
        help_text='Notificao recebida do orgao atuador'
    )
    memorando = models.FileField(
        upload_to='documentos/multas/memorandos/',
        blank=True,
        null=True,
        help_text='Memorando criado por FleetManager'
    )

    data_registro = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    conta_pagamento = models.ForeignKey(
        'ContaPagamento',
        on_delete=models.PROTECT,
        related_name='multas',
        help_text="Conta para pagamento da multa",
        null=True, blank=True
    )

    def clean(self):
        if self.status_multa == 'recebido' and not self.documento_recebido:
            raise ValidationError("É obrigatório anexar o documento com carimbo de recebido.")
        if self.status_pagamento == 'pago' and not self.comprovante_pagamento:
            raise ValidationError("É obrigatório anexar o comprovante de pagamento.")
        

    def save(self, *args, **kwargs):
        # Se for uma multa nova e o setor ainda não foi preenchido, copia do veículo
        if not self.pk and not self.setor:
            self.setor = str(self.veiculo.setor)
            self.setor_descricao = str(self.veiculo.setor.descricao)
        self.full_clean()  # garante validações
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.veiculo.placa} - {self.setor}"

    @property
    def valor(self):
        return self.infracao.valor

    @property
    def gravidade(self):
        return self.infracao.gravidade

class TermoResponsabilidade(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='documentos/veiculos/termo/', blank=True, null=True)
    data_assinatura = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()  # Adicione essa linha

    def __str__(self):
        return f"{self.veiculo} - {self.motorista}"


class InfracaoTransito(models.Model):
    descricao = models.CharField(max_length=255)  # Ex: "Avançar sinal vermelho"
    gravidade = models.CharField(max_length=50, choices=[
        ('leve', 'Leve'),
        ('media', 'Média'),
        ('grave', 'Grave'),
        ('gravissima', 'Gravíssima'),
    ])
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descricao} ({self.gravidade})"

class ContaPagamento(models.Model):
    banco = models.CharField(
        max_length=100,
        help_text="Nome do banco, ex: Banco do Brasil"
    )
    agencia = models.CharField(
        max_length=10,
        help_text="Número da agência, ex: 0000"
    )
    conta_corrente = models.CharField(
        max_length=20,
        help_text="Número da conta corrente, ex: 000000-0"
    )
    favorecido = models.CharField(
        max_length=200,
        default="Prefeitura Municipal de Lauro de Freitas – Secretaria de Administração",
        help_text="Nome do favorecido"
    )
    cnpj = models.CharField(
        max_length=18,
        help_text="CNPJ do favorecido, ex: XX.XXX.XXX/0001-XX"
    )

    def __str__(self):
        return f"{self.favorecido}"


