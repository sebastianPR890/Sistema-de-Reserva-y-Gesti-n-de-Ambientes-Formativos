from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .forms import BusquedaUsuarioForm, UsuarioEditForm 
from .models import Usuario
from django.db.models import Q 

def es_admin(user):
    return user.is_staff

@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    """Vista para listar, buscar y filtrar usuarios - solo accesible por administradores"""
    
    # 1. Inicializa el QuerySet de todos los usuarios (sin filtro de activo)
    usuarios = Usuario.objects.all().order_by('apellidos', 'nombres') 
    
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
@user_passes_test(es_admin)
def editar_usuario(request, pk):
    """
    Vista para editar un usuario existente. Solo accesible por administradores (is_staff).
    """
    # 1. Obtener el objeto Usuario o devolver 404
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        # 2. Rellenar el formulario con los datos de la petición y la instancia
        form = UsuarioEditForm(request.POST, instance=usuario)
        
        if form.is_valid():
            # 3. Guardar los cambios
            usuario = form.save(commit=False)
            # Asegurarnos que activo e is_active estén sincronizados
            usuario.is_active = usuario.activo
            usuario.save()
            messages.success(request, f'Usuario {usuario.nombre_completo} actualizado exitosamente.')
            # Redirigir a la lista
            return redirect('usuarios:lista_usuarios') 
        else:
            messages.error(request, '❌ Error al guardar los cambios. Revisa los campos.')
            
    else:
        # 4. Mostrar el formulario con los datos actuales
        form = UsuarioEditForm(instance=usuario)
        
    context = {
        'form': form,
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/editar_usuario.html', context)

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
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.telefono = request.POST.get('telefono')
        
        try:
            user.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
        except Exception as e:
            messages.error(request, f'Error al actualizar el perfil: {str(e)}')
    
    return render(request, 'usuarios/editar_perfil.html')
