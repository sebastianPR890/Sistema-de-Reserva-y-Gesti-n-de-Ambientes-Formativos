from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone # Importar timezone para consistencia

class Usuario(AbstractUser):
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
    
    # Sobrescribir campos de AbstractUser
    username = models.CharField(max_length=150, unique=True)  # Quitamos blank=True y null=True
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    
    # USERNAME_FIELD permanece como 'username' para compatibilidad con createsuperuser
    USERNAME_FIELD = 'username'
    # Agregamos documento como campo requerido
    REQUIRED_FIELDS = ['email', 'documento', 'nombres', 'apellidos'] 
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios' # Nombre de la tabla en la base de datos
        ordering = ['apellidos', 'nombres'] # Ordenamiento por defecto
    
    def save(self, *args, **kwargs):
        # Si no hay username, usar el documento
        if not self.username:
            self.username = self.documento
        if not self.first_name:
            self.first_name = self.nombres
        if not self.last_name:
            self.last_name = self.apellidos
        super().save(*args, **kwargs)
    
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    def puede_aprobar_reservas(self):
        return self.rol in ['coordinador', 'admin']
    
    def __str__(self):
        return f"{self.documento} - {self.nombre_completo()}"