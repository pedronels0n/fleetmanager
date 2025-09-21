from django import forms
from .models import Motorista, TermoResponsabilidade, Veiculo, Multa, Setor
from django.contrib.auth.models import User, Group

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = '__all__'
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'renavam': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'min':1900, 'max':2100}),
            'ano_modelo': forms.NumberInput(attrs={'class': 'form-control', 'min':1900, 'max':2100}),
            'chassi': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_frota': forms.Select(attrs={'class': 'form-select'}),
            'cor': forms.Select(attrs={'class': 'form-select'}),
            'tipo_modelo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_combustivel': forms.Select(attrs={'class': 'form-select'}),
            'crlv': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'seguro': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'motoristas': forms.SelectMultiple(attrs={'class': 'form-select', 'size':6}),
            'status_atual': forms.Select(attrs={'class': 'form-select'}),
            'setor': forms.Select(attrs={'class': 'form-select'}),
        }


class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = '__all__'
        widgets = {
            'cnh_validade': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'AAAA-MM-DD',
            }),
        }

class TermoResponsabilidadeForm(forms.ModelForm):

    # Formulario baseado no termo

    class Meta:
        model = TermoResponsabilidade
        fields = "__all__"


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_staff', 'is_active', 'grupos']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['grupos'])
        return user


class TrocaSetorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setores = Setor.objects.all()
        self.setor_map = {s.nome: s.descricao for s in setores}
        self.fields['setor'] = forms.ChoiceField(
            choices=[(s.nome, s.nome) for s in setores],
            label='Setor',
            required=True
        )
        self.fields['setor_descricao'].widget.attrs['readonly'] = True

    class Meta:
        model = Multa
        fields = ['setor', 'setor_descricao']

    def clean(self):
        cleaned_data = super().clean()
        setor_nome = cleaned_data.get('setor')
        cleaned_data['setor_descricao'] = self.setor_map.get(setor_nome, '')
        return cleaned_data

class MultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = [
            'numero_memorando',
            'auto_infracao',
            'veiculo',
            'setor',
            'setor_descricao',
            'motorista',
            'infracao',
            'data_hora_infracao',
            'local',
            'orgao_autuador',
            'prazo_pagamento',
            'status_multa',
            'status_pagamento',
            'documento_recebido',
            'comprovante_pagamento',
            'notificacao_infracao',
            'memorando',
            'conta_pagamento',
        ]
        widgets = {
            'data_hora_infracao': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'prazo_pagamento': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'status_multa': forms.Select(attrs={'class': 'form-select'}),
            'status_pagamento': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'setor': "Será preenchido automaticamente com o setor do veículo, mas pode ser ajustado.",
            'documento_recebido': "Obrigatório se o status da multa for 'Recebido'.",
            'comprovante_pagamento': "Obrigatório se o status do pagamento for 'Pago'.",
            'notificacao_infracao': "É obrigatório informar a notificação ao criar a multa.",
        }

    def clean(self):
        cleaned_data = super().clean()
        status_multa = cleaned_data.get("status_multa")
        status_pagamento = cleaned_data.get("status_pagamento")
        documento_recebido = cleaned_data.get("documento_recebido")
        comprovante_pagamento = cleaned_data.get("comprovante_pagamento")
        notificacao = cleaned_data.get("notificacao_infracao")

        # Se estiver criando (sem pk ainda) e não tiver notificação
        if not self.instance.pk and not notificacao:
            self.add_error('notificacao_infracao', "É obrigatório informar a notificação ao criar a multa.")

        if status_multa == 'recebido' and not documento_recebido:
            self.add_error('documento_recebido', "É obrigatório anexar o documento com carimbo de recebido.")

        if status_pagamento == 'pago' and not comprovante_pagamento:
            self.add_error('comprovante_pagamento', "É obrigatório anexar o comprovante de pagamento.")

        return cleaned_data
    
class AtualizarStatusMultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = ['status_multa', 'documento_recebido']
        widgets = {
            'status_multa': forms.Select(attrs={'class': 'form-select'}),
            'documento_recebido': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status_multa")
        documento = cleaned_data.get("documento_recebido")

        if status == "recebido" and not (documento or self.instance.documento_recebido):
            raise forms.ValidationError("Para marcar como recebido é necessário anexar o documento.")
        
        return cleaned_data
    
class PagamentoMultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = ['status_pagamento', 'comprovante_pagamento']
        widgets = {
            'status_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'comprovante_pagamento': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status_pagamento")
        comprovante = cleaned_data.get("comprovante_pagamento")

        # Se marcar como "pago", tem que anexar comprovante
        if status == "pago" and not (comprovante or self.instance.comprovante_pagamento):
            raise forms.ValidationError("Para marcar como pago é necessário anexar o comprovante.")

        return cleaned_data