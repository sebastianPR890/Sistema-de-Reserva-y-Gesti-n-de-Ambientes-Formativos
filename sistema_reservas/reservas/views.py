from django.utils.timezone import localtime
from django.utils import timezone
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseForbidden
from .models import Reserva
from notificaciones.models import Notificacion
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import pytz
from .forms import ReservaForm

def index(request):
    """Vista principal accesible para todos los usuarios."""
    return render(request, 'index.html')

@login_required
def lista_reservas(request):
    """Muestra la lista de reservas según el tipo de usuario."""
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
    """Permite crear una nueva reserva."""
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.save()
            Notificacion.crear(
                usuario=request.user,
                titulo='Reserva Creada',
                mensaje=f'Tu reserva ha sido creada y está pendiente de aprobación.',
                tipo='reserva'
            )
            messages.success(request, '¡Reserva creada exitosamente!')
            return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm()
    return render(request, 'reservas/crear_reserva.html', {'form': form})


@login_required
def editar_reserva(request, pk):
    """Permite editar una reserva existente."""
    reserva = get_object_or_404(Reserva, pk=pk)

    if reserva.usuario != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para editar esta reserva.")

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
                mensaje=f'Tu reserva ha sido actualizada correctamente.',
                tipo='reserva'
            )
            messages.success(request, '¡Reserva actualizada exitosamente!')
            return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'reservas/editar_reserva.html', {'form': form})


@login_required
def eliminar_reserva(request, pk):
    """Permite eliminar una reserva."""
    reserva = get_object_or_404(Reserva, pk=pk)

    if reserva.usuario != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para eliminar esta reserva.")

    if request.method == 'POST':
        fecha_inicio_str = reserva.fecha_inicio.strftime("%d/%m/%Y a las %H:%M")
        
        reserva.delete()
        Notificacion.crear(
            usuario=request.user,
            titulo='Reserva Eliminada',
            mensaje=f'Tu reserva del {fecha_inicio_str} ha sido eliminada.',
            tipo='reserva'
        )
        messages.success(request, 'Reserva eliminada correctamente.')
        return redirect('reservas:lista_reservas')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})

@login_required
def descargar_reporte_pdf(request):
    """Genera y descarga un reporte PDF de las reservas."""
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph("Reporte de Reservas", title_style))
    
    if request.user.is_staff:
        reservas = Reserva.objects.select_related('usuario', 'ambiente').all()
    else:
        reservas = Reserva.objects.filter(usuario=request.user).select_related('ambiente')
    
    data = [['Ambiente', 'Fecha Inicio', 'Fecha Fin', 'Estado']]
    for reserva in reservas:
        data.append([
            reserva.ambiente.nombre,
            reserva.fecha_inicio.strftime("%d/%m/%Y %H:%M"),
            reserva.fecha_fin.strftime("%d/%m/%Y %H:%M"),
            reserva.get_estado_display()
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'reporte_reservas_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf',
        content_type='application/pdf'
    )

def manual_usuario(request):
    """Muestra el manual de usuario en HTML."""
    return render(request, 'manual/manual_usuario.html')

def descargar_manual_pdf(request):
    """Retorna la vista HTML del manual de usuario."""
    return render(request, 'manual/manual_usuario.html')

@login_required
def aprobar_reserva(request, pk):
    """Aprueba una reserva específica."""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para aprobar reservas.")
        return redirect('reservas:lista_reservas')
    
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'aprobada'
    reserva.aprobada_por = request.user
    reserva.fecha_aprobacion = timezone.now()
    reserva.save()
    
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
    """Cancela una reserva específica."""
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para cancelar reservas.")
        return redirect('reservas:lista_reservas')
    
    reserva = get_object_or_404(Reserva, pk=pk)
    reserva.estado = 'cancelada'
    reserva.save()
    
    Notificacion.crear(
        usuario=reserva.usuario,
        titulo='Reserva Cancelada',
        mensaje=f'Tu reserva para el {reserva.fecha_inicio.strftime("%d/%m/%Y")} ha sido cancelada.',
        tipo='reserva'
    )
    
    messages.success(request, "Reserva cancelada exitosamente.")
    return redirect('reservas:lista_reservas')