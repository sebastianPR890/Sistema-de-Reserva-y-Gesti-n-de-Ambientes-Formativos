from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Usuario

# Create your views here.
@login_required
def lista_usuarios(request):
    """Muestra una lista de todos los usuarios activos."""
    usuarios = Usuario.objects.filter(activo=True).order_by('apellidos', 'nombres')
    context = {'usuarios': usuarios}
    return render(request, 'usuarios/lista_usuarios.html', context)

@login_required
def detalle_usuario(request, pk):
    """Muestra los detalles de un usuario específico."""
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, 'usuarios/detalle_usuario.html', {'usuario': usuario})
