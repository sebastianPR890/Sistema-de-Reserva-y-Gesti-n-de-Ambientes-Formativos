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