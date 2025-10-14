# usuarios/forms.py

from django import forms
from .models import Usuario # Se necesita importar el modelo Usuario

class BusquedaUsuarioForm(forms.Form):
    # Campo de búsqueda por texto (Nombre, Apellidos, Documento)
    busqueda = forms.CharField(
        required=False, 
        label='Nombre, Apellidos o Documento',
        widget=forms.TextInput(attrs={'placeholder': 'Escribe nombre, apellido o documento', 'class': 'form-control'})
    )
    
    # Campo de filtro por Rol
    rol = forms.ChoiceField(
        required=False,
        label='Filtrar por Rol',
        # *** CORRECCIÓN: Usamos Usuario.ROLES en lugar de ROL_CHOICES ***
        choices=[('', 'Todos los Roles')] + list(Usuario.ROLES), 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Campo de filtro por Estado
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[
            ('', 'Todos'),
            ('activo', 'Activos'),
            ('inactivo', 'Inactivos')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class UsuarioEditForm(forms.ModelForm):

    class Meta:
        model = Usuario
        # Campos que se permitirán editar. Excluimos 'password' y 'date_joined'
        fields = [
            'documento', 
            'nombres', 
            'apellidos', 
            'email', 
            'telefono', 
            'rol', 
            'activo', 
            'is_staff', 
            'is_superuser', 
            # Los campos username, first_name, last_name se manejan automáticamente por el save del modelo
        ] 
        widgets = {
            # El documento debe ser de solo lectura para evitar errores de unicidad
            'documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), 
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            # Checkboxes
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # Opcional: Para evitar que el usuario edite su propio documento (readonly)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que el documento siempre es de solo lectura en la edición
        if 'documento' in self.fields:
            self.fields['documento'].widget.attrs['readonly'] = 'readonly'