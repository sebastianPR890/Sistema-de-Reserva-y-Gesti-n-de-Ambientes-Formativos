from django import forms
from .models import Equipo, MovimientoEquipo

class EquipoForm(forms.ModelForm):
    """
    Formulario para crear y actualizar un Equipo.
    """
    class Meta:
        model = Equipo
        fields = [
            'codigo', 'nombre', 'descripcion', 'marca', 'modelo', 'serie',
            'ambiente', 'estado', 'responsable', 'fecha_adquisicion',
            'valor', 'activo'
        ]
        widgets = {
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date'}),
        }
    
class BusquedaEquipoForm(forms.Form):
    """
    Formulario para buscar y filtrar la lista de equipos.
    """
    busqueda = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por código, nombre o serie...',
            'class': 'form-control'
        })
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Equipo.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    activo = forms.BooleanField(required=False, initial=True, label='Solo activos')
    
class MovimientoEquipoForm(forms.ModelForm):
    """
    Formulario para registrar un movimiento de equipo.
    """
    class Meta:
        model = MovimientoEquipo
        fields = [
            'equipo', 'tipo_movimiento', 'ambiente_origen', 
            'ambiente_destino', 'usuario_responsable', 'observaciones',
            'autorizado_por'
        ]