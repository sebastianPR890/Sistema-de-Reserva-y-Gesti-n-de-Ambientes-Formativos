from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Notificacion(models.Model):
    TIPOS = (
        ('reserva', 'Reserva'),
        ('equipo', 'Equipo'),
        ('sistema', 'Sistema'),
        ('alerta', 'Alerta'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPOS, default='sistema')
    leida = models.BooleanField(default=False)
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        db_table = 'notificaciones'
        ordering = ['-fecha_de_creacion']
    
    @classmethod
    def crear(cls, usuario, titulo, mensaje, tipo='sistema'):
        """crea una notificación"""
        return cls.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo
        )
    def marcar_como_leida(self):
        """marca la notificación como leída"""
        self.leida = True
        self.save()
    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre_completo()}"