from django.contrib import admin
from .models import *
from import_export.admin import ExportMixin, ImportExportModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget
from .models import Veiculo, Setor, Motorista
from import_export.widgets import DateWidget

# Registros normais
admin.site.register(Setor)
admin.site.register(ManutencaoVeiculo)
admin.site.register(Multa)
admin.site.register(TermoResponsabilidade)
admin.site.register(ContaPagamento)

# Recurso de importação
class VeiculoResource(resources.ModelResource):
    setor = fields.Field(
        column_name='setor',
        attribute='setor',
        widget=ForeignKeyWidget(Setor, field='nome')
    )

    class Meta:
        model = Veiculo
        import_id_fields = ['placa']
        fields = (
            'placa', 'renavam', 'marca', 'modelo', 'ano', 'ano_modelo', 'chassi',
            'tipo_frota', 'cor', 'tipo_modelo', 'tipo_combustivel', 'status_atual', 'setor'
        )
        skip_unchanged = True
        report_skipped = True


class VeiculoAdmin(ImportExportModelAdmin):
    resource_class = VeiculoResource
    list_display = ('placa', 'modelo', 'status_atual', 'setor')
    search_fields = ('placa', 'modelo', 'renavam', 'chassi')


admin.site.register(Veiculo, VeiculoAdmin)

class MotoristaResource(resources.ModelResource):
    data_nacimento = fields.Field(
        column_name='data_nacimento',
        attribute='data_nacimento',
        widget=DateWidget(format='%d/%m/%Y')
    )
    cnh_validade = fields.Field(
        column_name='cnh_validade',
        attribute='cnh_validade',
        widget=DateWidget(format='%d/%m/%Y')
    )
    
    class Meta:
        model = Motorista
        import_id_fields = ['cpf']
        fields = (
            'nome', 'cpf', 'rg', 'telefone', 'data_nacimento',
            'status_atual', 'cnh_numero', 'cnh_validade',
            'cnh_categoria', 'cnh_arquivo'
        )
        skip_unchanged = True
        report_skipped = True

class MotoristaAdmin(ImportExportModelAdmin):
    resource_class = MotoristaResource
    list_display = ('nome', 'cpf', 'telefone', 'status_atual', 'cnh_categoria')
    search_fields = ('nome', 'cpf', 'cnh_numero')
    list_filter = ('status_atual', 'cnh_categoria')
    ordering = ('nome',)

admin.site.register(Motorista, MotoristaAdmin)


class InfracaoTransitoResource(resources.ModelResource):
    class Meta:
        model = InfracaoTransito
        fields = ('descricao', 'gravidade', 'valor')
        import_id_fields = ('descricao',)  # opcional: usa descricao como referência ao atualizar

class InfracaoTransitoAdmin(ImportExportModelAdmin):
    resource_class = InfracaoTransitoResource
    list_display = ('descricao', 'gravidade', 'valor')
    search_fields = ('descricao',)
    list_filter = ('gravidade',)

admin.site.register(InfracaoTransito, InfracaoTransitoAdmin)

admin.site.register(Abastecimento)