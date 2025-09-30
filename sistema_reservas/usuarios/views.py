from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Usuario

def es_admin(user):
    return user.is_staff

# Create your views here.
@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    """Vista para listar usuarios - solo accesible por administradores"""
    usuarios = Usuario.objects.filter(activo=True).order_by('apellidos', 'nombres')
    context = {'usuarios': usuarios}
    return render(request, 'usuarios/lista_usuarios.html', context)

@login_required
@user_passes_test(es_admin)
def detalle_usuario(request, pk):
    """Vista para ver detalles de usuario - solo accesible por administradores"""
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/detalle_usuario.html', {'usuario': usuario})
