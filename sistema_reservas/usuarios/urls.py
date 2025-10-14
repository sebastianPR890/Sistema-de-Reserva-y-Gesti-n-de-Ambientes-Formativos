from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('<int:pk>/', views.detalle_usuario, name='detalle_usuario'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    # Aquí puedes añadir URLs para crear, editar y eliminar usuarios en el futuro

    path('<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
]
