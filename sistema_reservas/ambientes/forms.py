# ambientes/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Ambiente

class AmbienteForm(forms.ModelForm):
    # Campos para computadores
    tiene_computadores = forms.BooleanField(required=False, label='Tiene Computadores')
    numero_computadores = forms.IntegerField(
        required=False, 
        min_value=0, 
        label='Número de Computadores',
        widget=forms.NumberInput(attrs={'placeholder': '0', 'class': 'form-control'})
    )
    computadores_danados = forms.IntegerField(
        required=False, 
        min_value=0, 
        label='Computadores Dañados',
        widget=forms.NumberInput(attrs={'placeholder': '0', 'class': 'form-control'})
    )
    
    # Campos para escritorios
    tiene_escritorios = forms.BooleanField(required=False, label='Tiene Escritorios')
    cantidad_escritorios = forms.IntegerField(
        required=False, 
        min_value=0, 
        label='Cantidad de Escritorios',
        widget=forms.NumberInput(attrs={'placeholder': '0', 'class': 'form-control'})
    )
    escritorios_danados = forms.IntegerField(
        required=False, 
        min_value=0, 
        label='Escritorios Dañados',
        widget=forms.NumberInput(attrs={'placeholder': '0', 'class': 'form-control'})
    )
    
    # Tablero digital
    tiene_tablero_digital = forms.BooleanField(required=False, label='Tiene Tablero Digital')
    
    # Observaciones
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Observaciones...'}),
        required=False,
        label='Observaciones'
    )
    
    class Meta:
        model = Ambiente
        fields = ['codigo', 'nombre', 'descripcion', 'capacidad', 'tipo', 'ubicacion', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej: A-101', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del ambiente', 'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'placeholder': 'Ubicación', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar datos existentes si estamos editando
        if self.instance and self.instance.pk and self.instance.recursos:
            recursos = self.instance.recursos
            self.fields['tiene_computadores'].initial = recursos.get('computadores', False)
            self.fields['numero_computadores'].initial = recursos.get('numero_computadores', 0)
            self.fields['computadores_danados'].initial = recursos.get('computadores_danados', 0)
            self.fields['tiene_escritorios'].initial = recursos.get('escritorios', False)
            self.fields['cantidad_escritorios'].initial = recursos.get('cantidad_escritorios', 0)
            self.fields['escritorios_danados'].initial = recursos.get('escritorios_danados', 0)
            self.fields['tiene_tablero_digital'].initial = recursos.get('tablero_digital', False)
            self.fields['observaciones'].initial = recursos.get('observaciones', '')
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            codigo = codigo.upper().strip()
            if Ambiente.objects.filter(codigo=codigo).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise ValidationError('Ya existe un ambiente con este código.')
        return codigo
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar computadores
        tiene_computadores = cleaned_data.get('tiene_computadores')
        numero_computadores = cleaned_data.get('numero_computadores', 0)
        computadores_danados = cleaned_data.get('computadores_danados', 0)
        
        if tiene_computadores:
            if not numero_computadores or numero_computadores <= 0:
                raise ValidationError('Si tiene computadores, debe especificar cuántos.')
            if computadores_danados > numero_computadores:
                raise ValidationError('Los computadores dañados no pueden ser más que el total.')
        
        # Validar escritorios
        tiene_escritorios = cleaned_data.get('tiene_escritorios')
        cantidad_escritorios = cleaned_data.get('cantidad_escritorios', 0)
        escritorios_danados = cleaned_data.get('escritorios_danados', 0)
        
        if tiene_escritorios:
            if not cantidad_escritorios or cantidad_escritorios <= 0:
                raise ValidationError('Si tiene escritorios, debe especificar cuántos.')
            if escritorios_danados > cantidad_escritorios:
                raise ValidationError('Los escritorios dañados no pueden ser más que el total.')
            
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Construir JSON de recursos
        recursos = {
            'computadores': self.cleaned_data.get('tiene_computadores', False),
            'numero_computadores': self.cleaned_data.get('numero_computadores', 0) if self.cleaned_data.get('tiene_computadores') else 0,
            'computadores_danados': self.cleaned_data.get('computadores_danados', 0) if self.cleaned_data.get('tiene_computadores') else 0,
            'escritorios': self.cleaned_data.get('tiene_escritorios', False),
            'cantidad_escritorios': self.cleaned_data.get('cantidad_escritorios', 0) if self.cleaned_data.get('tiene_escritorios') else 0,
            'escritorios_danados': self.cleaned_data.get('escritorios_danados', 0) if self.cleaned_data.get('tiene_escritorios') else 0,
            'tablero_digital': self.cleaned_data.get('tiene_tablero_digital', False),
            'observaciones': self.cleaned_data.get('observaciones', ''),
        }
        
        instance.recursos = recursos
        
        if commit:
            instance.save()
        return instance

class BusquedaAmbienteForm(forms.Form):
    busqueda = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por código, nombre o ubicación...',
            'class': 'form-control'
        })
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Ambiente.TIPOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    capacidad_min = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Capacidad mínima',
            'class': 'form-control'
        })
    )
    solo_activos = forms.BooleanField(required=False, initial=True, label='Solo activos')
    con_computadores = forms.BooleanField(required=False, label='Con computadores')
    con_escritorios = forms.BooleanField(required=False, label='Con escritorios')
    con_tablero_digital = forms.BooleanField(required=False, label='Con tablero digital')