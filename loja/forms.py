from django import forms
from .models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto', 'cpf', 'telefone', 'endereco']
        widgets = {
            'endereco': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Rua, número, bairro e cidade...'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
        }