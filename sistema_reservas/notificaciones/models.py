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
        """crea una notificación y envía un correo electrónico HTML"""
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        notificacion = cls.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo
        )

        # Renderizar el template HTML
        html_content = render_to_string('email/notification.html', {'titulo': titulo, 'mensaje': mensaje})
        # Crear una versión de texto plano como fallback
        text_content = strip_tags(html_content)

        # Enviar correo electrónico
        msg = EmailMultiAlternatives(
            titulo,
            text_content,
            'noreply@sistemareservas.com',
            [usuario.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        return notificacion
    def marcar_como_leida(self):
        """marca la notificación como leída"""
        self.leida = True
        self.save()
    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre_completo()}"