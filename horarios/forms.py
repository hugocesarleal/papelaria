from django import forms
from .models import HorarioFuncionamento, ExcecaoHorario

class HorarioFuncionamentoForm(forms.ModelForm):
    class Meta:
        model = HorarioFuncionamento
        fields = ['dia_semana', 'abertura', 'fechamento']
        widgets = {
            'abertura': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'fechamento': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

class ExcecaoHorarioForm(forms.ModelForm):
    class Meta:
        model = ExcecaoHorario
        fields = ['horario', 'data']
        widgets = {
            'data': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['horario'].queryset = HorarioFuncionamento.objects.all().order_by('dia_semana', 'abertura')