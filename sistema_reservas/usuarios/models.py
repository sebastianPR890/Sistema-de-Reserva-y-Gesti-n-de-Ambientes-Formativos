from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Usuario(AbstractUser):
    """Modelo personalizado de usuario que extiende AbstractUser."""
    
    ROLES = [
        ('instructor', 'Instructor'),
        ('administrativo', 'Administrativo'),
        ('coordinador', 'Coordinador'),
        ('admin', 'Administrador'),
    ]
    
    documento = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[RegexValidator(regex=r'^\d+$', message='Solo números')]
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='instructor')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'documento', 'nombres', 'apellidos'] 
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'
        ordering = ['apellidos', 'nombres']
    
    def save(self, *args, **kwargs):
        """Sincroniza campos antes de guardar el usuario."""
        if not self.username:
            self.username = self.documento
        if not self.first_name:
            self.first_name = self.nombres
        if not self.last_name:
            self.last_name = self.apellidos
            
        self.is_active = self.activo
        super().save(*args, **kwargs)
    
    def nombre_completo(self):
        """Retorna el nombre completo del usuario."""
        return f"{self.nombres} {self.apellidos}"
    
    def puede_aprobar_reservas(self):
        """Verifica si el usuario puede aprobar reservas."""
        return self.rol in ['coordinador', 'admin']
    
    def __str__(self):
        return f"{self.documento} - {self.nombre_completo()}"