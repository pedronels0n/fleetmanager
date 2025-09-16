from django import forms
from .models import Motorista, TermoResponsabilidade, Veiculo

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
