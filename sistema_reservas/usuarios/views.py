from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .forms import BusquedaUsuarioForm
from .models import Usuario
from django.db.models import Q 

def es_admin(user):
    return user.is_staff

@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    """Vista para listar, buscar y filtrar usuarios - solo accesible por administradores"""
    
    # 1. Inicializa el QuerySet de usuarios activos
    usuarios = Usuario.objects.filter(activo=True).order_by('apellidos', 'nombres') 
    
    # 2. Inicializa el formulario de búsqueda con los parámetros GET
    form_busqueda = BusquedaUsuarioForm(request.GET)
    
    # 3. Aplica los filtros SOLO si el formulario es válido
    if form_busqueda.is_valid():
        cleaned_data = form_busqueda.cleaned_data
        
        # 1. Filtro de Búsqueda por Texto (Nombre, Apellidos o Documento)
        # *** CLAVE DE LA CORRECCIÓN: Usar .get() para evitar KeyError ***
        busqueda = cleaned_data.get('busqueda') 
        if busqueda:
            # Filtra por nombres, apellidos o documento (búsqueda combinada OR)
            usuarios = usuarios.filter(
                Q(nombres__icontains=busqueda) | 
                Q(apellidos__icontains=busqueda) | 
                Q(documento__icontains=busqueda) 
            )
            
        # 2. Filtro por Rol
        # *** CLAVE DE LA CORRECCIÓN: Usar .get() ***
        rol = cleaned_data.get('rol') 
        # El campo rol del formulario devuelve una cadena vacía ('') si se selecciona 'Todos los Roles'
        if rol: 
            usuarios = usuarios.filter(rol=rol)

    context = {
        'usuarios': usuarios,
        'form_busqueda': form_busqueda # Pasar el formulario al template
    }
    
    return render(request, 'usuarios/lista_usuarios.html', context)

@login_required
@user_passes_test(es_admin)
def detalle_usuario(request, pk):
    """Vista para ver detalles de usuario - solo accesible por administradores"""
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/detalle_usuario.html', {'usuario': usuario})

@login_required 
def perfil_usuario(request):
    """
    Vista que muestra los detalles del usuario logueado. 
    Solo es accesible si el usuario ha iniciado sesión.
    """
    context = {
        'user': request.user,
    }
    # Renderiza la nueva plantilla perfil_usuario.html
    return render(request, 'usuarios/perfil_usuario.html', context)

@login_required
def editar_perfil(request):
    return render(request, 'usuarios/editar_perfil.html', {})

@login_required
@user_passes_test(es_admin)
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.activo = False
        usuario.save()
        messages.success(request, f'Usuario {usuario.nombre_completo} ha sido desactivado.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/eliminar_usuario_confirm.html', {'usuario': usuario})
