from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('<int:pk>/', views.detalle_usuario, name='detalle_usuario'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    # Aquí puedes añadir URLs para crear, editar y eliminar usuarios en el futuro
]
