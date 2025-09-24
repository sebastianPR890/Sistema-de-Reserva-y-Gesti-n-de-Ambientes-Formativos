from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Reserva
from notificaciones.models import Notificacion
from .forms import ReservaForm

@login_required
def lista_reservas(request):
    # Solo muestra las reservas del usuario logueado, a menos que sea superusuario
    if request.user.is_superuser:
        reservas = Reserva.objects.select_related('ambiente', 'usuario').all()
    else:
        reservas = Reserva.objects.filter(usuario=request.user).select_related('ambiente')
        
    return render(request, 'reservas/lista_reservas.html', {'reservas': reservas})

@login_required
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user # Asigna el usuario actual a la reserva
            reserva.save()
            Notificacion.crear(
                usuario=request.user,
                titulo='Reserva Creada',
                mensaje=f'Tu reserva para el ambiente "{reserva.ambiente.nombre}" ha sido creada y está pendiente de aprobación.',
                tipo='reserva'
            )
            messages.success(request, '¡Reserva creada exitosamente!')
            return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm()
    return render(request, 'reservas/crear_reserva.html', {'form': form})

@login_required
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    # Solo el dueño de la reserva o un superusuario pueden editar
    if reserva.usuario != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para editar esta reserva.")

    # Lógica del modelo para verificar si la reserva es editable
    if not reserva.puede_ser_editada():
        messages.error(request, 'Esta reserva ya no puede ser editada.')
        return redirect('reservas:lista_reservas')

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            Notificacion.crear(
                usuario=request.user,
                titulo='Reserva Actualizada',
                mensaje=f'Tu reserva para "{reserva.ambiente.nombre}" ha sido actualizada correctamente.',
                tipo='reserva'
            )
            messages.success(request, '¡Reserva actualizada exitosamente!')
            return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'reservas/editar_reserva.html', {'form': form})

@login_required
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    # Solo el dueño de la reserva o un superusuario pueden eliminar
    if reserva.usuario != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para eliminar esta reserva.")

    if request.method == 'POST':
        # Guardamos los datos para la notificación antes de borrar
        ambiente_nombre = reserva.ambiente.nombre
        fecha_inicio_str = reserva.fecha_inicio.strftime("%d/%m/%Y a las %H:%M")
        
        reserva.delete()
        Notificacion.crear(
            usuario=request.user,
            titulo='Reserva Eliminada',
            mensaje=f'Tu reserva para el ambiente "{ambiente_nombre}" del {fecha_inicio_str} ha sido eliminada.',
            tipo='reserva'
        )
        messages.success(request, 'Reserva eliminada correctamente.')
        return redirect('reservas:lista_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})
