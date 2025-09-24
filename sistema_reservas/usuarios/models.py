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
    
    # Sobrescribir campos de AbstractUser para que sean opcionales y se deriven del documento
    # Esto es para evitar conflictos si se usan en formularios de registro,
    # aunque los rellenamos en save()
    username = models.CharField(max_length=150, unique=True, blank=True, null=True) 
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    
    # Email de AbstractUser ya es único, no necesitamos redefinirlo
    # email = models.EmailField(_("email address"), blank=True) # Ya está en AbstractUser

    USERNAME_FIELD = 'documento'
    # QUITAMOS 'nombres', 'apellidos' de REQUIRED_FIELDS porque se derivarán del modelo.
    # El email es requerido por AbstractUser, y si lo queremos en el superusuario, lo dejamos.
    REQUIRED_FIELDS = ['email'] 
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios' # Nombre de la tabla en la base de datos
        ordering = ['apellidos', 'nombres'] # Ordenamiento por defecto
    
    def save(self, *args, **kwargs):
        # Asegurarse de que el username y los nombres de AbstractUser se sincronicen con nuestros campos
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