# reservas/models.py
from django.db import models
from django.conf import settings # Para referenciar AUTH_USER_MODEL
from django.utils import timezone
from django.core.exceptions import ValidationError # Para validaciones del modelo
#from ambientes.models import Ambiente # Ya no es importación local
#from ambientes.models import Ambiente # ¡IMPORTANTE! Descomentar después de crear la app 'ambientes'

class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    # CAMBIO: on_delete=models.PROTECT para evitar borrados accidentales de Ambiente/Usuario
    # ambiente = models.ForeignKey(Ambiente, on_delete=models.PROTECT, related_name='reservas')
    ambiente = models.ForeignKey('ambientes.Ambiente', on_delete=models.PROTECT, related_name='reservas') # Usamos string para evitar importación circular
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reservas')
    
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    proposito = models.TextField()
    numero_asistentes = models.PositiveIntegerField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True)
    aprobada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reservas_aprobadas'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        db_table = 'reservas'
        ordering = ['-fecha_creacion']
    
    def clean(self):
        # Validar que la fecha de fin sea posterior a la de inicio
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
        
        # Validar que la fecha de inicio no sea en el pasado para nuevas reservas
        if self.pk is None and self.fecha_inicio and self.fecha_inicio < timezone.now():
            raise ValidationError('No se puede crear una reserva con fecha de inicio en el pasado.')
        
        # Validar que no haya solapamiento con otras reservas aprobadas
        # if self.ambiente and self.fecha_inicio and self.fecha_fin:
        #     if not self.ambiente.esta_disponible(self.fecha_inicio, self.fecha_fin, exclude_reserva_id=self.pk):
        #         raise ValidationError('El ambiente no está disponible en el horario seleccionado.')
    
    def save(self, *args, **kwargs):
        self.full_clean() # Ejecuta las validaciones del método clean() antes de guardar
        super().save(*args, **kwargs)

    def duracion_horas(self):
        """Calcula la duración de la reserva en horas"""
        if self.fecha_fin and self.fecha_inicio:
            delta = self.fecha_fin - self.fecha_inicio
            return delta.total_seconds() / 3600
        return 0
    
    def puede_ser_editada(self):
        """Verifica si la reserva puede ser editada"""
        return self.estado in ['pendiente', 'aprobada'] and self.fecha_inicio > timezone.now()
    
    def puede_ser_cancelada(self):
        """Verifica si la reserva puede ser cancelada"""
        return self.estado in ['pendiente', 'aprobada'] and self.fecha_inicio > timezone.now()
    
    def aprobar(self, usuario_aprobador):
        """Aprueba la reserva"""
        if usuario_aprobador and usuario_aprobador.puede_aprobar_reservas():
            self.estado = 'aprobada'
            self.aprobada_por = usuario_aprobador
            self.fecha_aprobacion = timezone.now()
            self.save()
            return True
        return False
    
    def rechazar(self, observaciones=''):
        """Rechaza la reserva"""
        self.estado = 'rechazada'
        if observaciones:
            self.observaciones = observaciones
        self.save()
    
    def __str__(self):
        # return f"Reserva {self.id} - {self.ambiente.nombre} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"
        return f"Reserva {self.id} por {self.usuario} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"