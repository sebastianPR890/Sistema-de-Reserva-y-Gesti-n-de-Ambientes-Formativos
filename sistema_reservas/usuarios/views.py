from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .forms import BusquedaUsuarioForm, UsuarioEditForm 
from .models import Usuario
from django.db.models import Q 

def es_admin(user):
    """Verifica si un usuario tiene permisos de administrador."""
    return user.is_staff

@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    """Muestra lista de usuarios con opciones de búsqueda y filtrado."""
    usuarios = Usuario.objects.all().order_by('apellidos', 'nombres') 
    form_busqueda = BusquedaUsuarioForm(request.GET)
    
    if form_busqueda.is_valid():
        cleaned_data = form_busqueda.cleaned_data
        
        busqueda = cleaned_data.get('busqueda') 
        if busqueda:
            usuarios = usuarios.filter(
                Q(nombres__icontains=busqueda) | 
                Q(apellidos__icontains=busqueda) | 
                Q(documento__icontains=busqueda) 
            )
            
        rol = cleaned_data.get('rol') 
        if rol: 
            usuarios = usuarios.filter(rol=rol)

    context = {
        'usuarios': usuarios,
        'form_busqueda': form_busqueda
    }
    
    return render(request, 'usuarios/lista_usuarios.html', context)

@login_required
@user_passes_test(es_admin)
def detalle_usuario(request, pk):
    """Muestra los detalles de un usuario específico."""
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/detalle_usuario.html', {'usuario': usuario})

@login_required
@user_passes_test(es_admin)
def editar_usuario(request, pk):
    """Permite editar los datos de un usuario existente."""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = usuario.activo
            usuario.save()
            messages.success(request, f'Usuario {usuario.nombre_completo} actualizado exitosamente.')
            return redirect('usuarios:lista_usuarios') 
        else:
            messages.error(request, '❌ Error al guardar los cambios. Revisa los campos.')
            
    else:
        form = UsuarioEditForm(instance=usuario)
        
    context = {
        'form': form,
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/editar_usuario.html', context)

@login_required 
def perfil_usuario(request):
    """Muestra el perfil del usuario autenticado."""
    context = {
        'user': request.user,
    }
    return render(request, 'usuarios/perfil_usuario.html', context)

@login_required
def editar_perfil(request):
    """Permite al usuario editar su propio perfil."""
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
