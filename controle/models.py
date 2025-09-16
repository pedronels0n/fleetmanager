from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from django.conf import settings

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
    
class Multa(models.Model):
    # Veículo vinculado à multa
    veiculo = models.ForeignKey(
        'Veiculo', 
        on_delete=models.CASCADE,         # Se o veículo for deletado, a multa também será removida
        related_name='multas'             # Permite acessar todas as multas de um veículo via veiculo.multas.all()
    )
    
    # Motorista vinculado à multa (opcional)
    motorista = models.ForeignKey(
        'Motorista', 
        on_delete=models.SET_NULL,        # Se o motorista for deletado, o campo será definido como NULL
        null=True,                        # Permite que o campo fique vazio
        blank=True,                       # Permite que o campo fique vazio em formulários/admin
        related_name='multas'             # Permite acessar todas as multas de um motorista via motorista.multas.all()
    )
    
    # Dados da infração
    data_infracao = models.DateField(
        default=timezone.now,             # Data da infração, padrão é a data atual
        help_text="Data em que a infração ocorreu"
    )
    local = models.CharField(
        max_length=200, 
        help_text="Local onde a infração foi registrada"
    )
    orgao_autuador = models.CharField(
        max_length=100, 
        help_text="Órgão que aplicou a multa"
    )
    valor = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Valor da multa em reais"
    )
    natureza = models.CharField(
        max_length=100, 
        help_text="Natureza da infração, ex: Estacionamento irregular, excesso de velocidade"
    )
    pontos = models.PositiveIntegerField(
        default=0, 
        help_text="Número de pontos na CNH referente à infração"
    )

    # Documento da multa (upload de PDF ou imagem)
    documento = models.FileField(
        upload_to='documentos/multas/',   # Pasta onde o arquivo será salvo
        blank=True,                        # Permite que o campo fique vazio
        null=True                           # Permite que o campo seja nulo no banco
    )

    # Data de registro no sistema
    data_registro = models.DateTimeField(
        auto_now_add=True,                 # Preenche automaticamente com a data/hora de criação
        help_text="Data e hora do registro da multa no sistema"
    )

    def __str__(self):
        """
        Representação do objeto como string.
        Exibe placa do veículo, natureza da infração e data.
        Útil para visualização no admin e listas.
        """
        return f"{self.veiculo.placa} - {self.natureza} em {self.data_infracao}"

class TermoResponsabilidade(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    motorista = models.ForeignKey(Motorista, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='documentos/veiculos/termo/', blank=True, null=True)
    data_assinatura = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()  # Adicione essa linha

    def __str__(self):
        return f"{self.veiculo} - {self.motorista}"
