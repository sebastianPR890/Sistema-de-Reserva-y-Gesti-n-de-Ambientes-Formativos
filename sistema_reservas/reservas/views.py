from django.utils.timezone import localtime
from django.utils import timezone
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseForbidden
from .models import Reserva
from notificaciones.models import Notificacion
from django.template.loader import get_template
from .forms import ReservaForm
from xhtml2pdf import pisa
import pytz

def index(request):
    """Vista del index accesible para todos los usuarios."""
    return render(request, 'index.html')

# Proteger todas las demás vistas
@login_required
def lista_reservas(request):
    # Determinar qué reservas mostrar basado en el tipo de usuario
    if request.user.is_staff:
        reservas = Reserva.objects.select_related('usuario', 'ambiente').all()
        user_type = 'admin'
    else:
        reservas = Reserva.objects.select_related('ambiente').filter(usuario=request.user)
        user_type = 'user'
    
    # Contadores para el dashboard
    total_reservas = reservas.count()
    reservas_pendientes = reservas.filter(estado='pendiente').count()
    reservas_aprobadas = reservas.filter(estado='aprobada').count()
    reservas_canceladas = reservas.filter(estado='cancelada').count()
    
    context = {
        'reservas': reservas,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_aprobadas': reservas_aprobadas,
        'reservas_canceladas': reservas_canceladas,
        'user_type': user_type,
    }
    
    return render(request, 'reservas/lista_reservas.html', context)


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
                mensaje=f'Tu reserva ha sido creada y está pendiente de aprobación.', # Mensaje sin ambiente.nombre
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
                mensaje=f'Tu reserva ha sido actualizada correctamente.', # Mensaje sin ambiente.nombre
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
        # ambiente_nombre = reserva.ambiente.nombre
        fecha_inicio_str = reserva.fecha_inicio.strftime("%d/%m/%Y a las %H:%M")
        
        reserva.delete()
        Notificacion.crear(
            usuario=request.user,
            titulo='Reserva Eliminada',
            mensaje=f'Tu reserva del {fecha_inicio_str} ha sido eliminada.', # Mensaje sin ambiente_nombre
            tipo='reserva'
        )
        messages.success(request, 'Reserva eliminada correctamente.')
        return redirect('reservas:lista_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})

@login_required
def descargar_reporte_pdf(request):
    # --- INICIO: Solución Naive para Evitar el Desfase de la Fecha de Generación ---
    
    # 1. Obtener la hora actual en la zona local (UTC-5)
    # **Nota:** Asumimos que tu hora local es UTC-5 (America/Bogota)
    local_tz = pytz.timezone('America/Bogota') 
    
    # 2. Obtener la hora actual en UTC
    fecha_utc = timezone.now()
    
    # 3. Convertir a la hora local, obteniendo un objeto *aware* (consciente de la zona)
    fecha_reporte_aware = fecha_utc.astimezone(local_tz)

    # 4. Convertir el objeto *aware* a un objeto *naive* (sin zona horaria)
    fecha_reporte_local = fecha_reporte_aware.replace(tzinfo=None) 
    
    # --- FIN: Solución Naive ---
    
    # Lógica para obtener las reservas a reportar
    if request.user.is_superuser:
        reservas = Reserva.objects.select_related('usuario', 'ambiente').all()
    else:
        reservas = Reserva.objects.filter(usuario=request.user).select_related('ambiente')
    
    # Contexto para la plantilla PDF
    contexto = {
        'reservas': reservas,
        'request': request,
        'now': fecha_reporte_local, # <-- Usamos el objeto datetime Naive corregido
    }
    
    # Obtener el template
    template = get_template('reservas/reporte_reservas_pdf.html')
    html = template.render(contexto)
    
    # Crear el buffer de bytes para el PDF
    buffer = io.BytesIO() # <-- Aquí se define 'buffer' en minúsculas
    
    # Generar el PDF
    pisa_status = pisa.CreatePDF(
        html,
        dest=buffer,
        link_callback=None
    )

    if pisa_status.err:
        messages.error(request, 'Ocurrió un error al generar el reporte PDF.')
        return redirect('reservas:lista_reservas')

    # Devolver el PDF como una respuesta de archivo descargable
    buffer.seek(0) # <-- Corregido para usar 'buffer' en minúsculas
    filename = f"reporte_reservas_{fecha_reporte_local.strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return FileResponse(
        buffer, 
        as_attachment=True, 
        filename=filename,
        content_type='application/pdf'
    )

def manual_usuario(request):
    """Vista para mostrar el manual de usuario en HTML."""
    return render(request, 'manual/manual_usuario.html')

def descargar_manual_pdf(request):
    """Vista para generar y descargar el manual de usuario en PDF."""
    # Obtener el template
    template = get_template('manual/manual_usuario.html')
    context = {} # El manual no necesita contexto dinámico por ahora
    html = template.render(context)
    
    # Crear el buffer de bytes para el PDF
    buffer = io.BytesIO()
    
    # Generar el PDF
    pisa_status = pisa.CreatePDF(
        html,
        dest=buffer
    )

    if pisa_status.err:
        messages.error(request, 'Ocurrió un error al generar el manual en PDF.')
        return redirect('reservas:manual_usuario') # Redirigir a la página del manual si hay error

    # Devolver el PDF como una respuesta de archivo descargable
    buffer.seek(0)
    filename = f"manual_de_usuario_sena.pdf"
    
    return FileResponse(
        buffer, 
        as_attachment=True, 
        filename=filename,
        content_type='application/pdf'
    )

@login_required
def aprobar_reserva(request, pk):
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para aprobar reservas.")
        return redirect('reservas:lista_reservas')
    
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'aprobada'
    reserva.aprobada_por = request.user
    reserva.fecha_aprobacion = timezone.now()
    reserva.save()
    
    # Crear notificación para el usuario
    Notificacion.crear(
        usuario=reserva.usuario,
        titulo='Reserva Aprobada',
        mensaje=f'Tu reserva para el {reserva.fecha_inicio.strftime("%d/%m/%Y")} ha sido aprobada.',
        tipo='reserva'
    )
    
    messages.success(request, "Reserva aprobada exitosamente.")
    return redirect('reservas:lista_reservas')

@login_required
def cancelar_reserva(request, pk):
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para cancelar reservas.")
        return redirect('reservas:lista_reservas')
    
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'cancelada'
    reserva.save()
    
    # Crear notificación para el usuario
    Notificacion.crear(
        usuario=reserva.usuario,
        titulo='Reserva Cancelada',
        mensaje=f'Tu reserva para el {reserva.fecha_inicio.strftime("%d/%m/%Y")} ha sido cancelada.',
        tipo='reserva'
    )
    
    messages.success(request, "Reserva cancelada exitosamente.")
    return redirect('reservas:lista_reservas')