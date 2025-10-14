from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.index, name='index'),  # Añadir name='index'
    path('reservas/', views.lista_reservas, name='lista_reservas'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('<int:pk>/editar/', views.editar_reserva, name='editar_reserva'),
    path('<int:pk>/eliminar/', views.eliminar_reserva, name='eliminar_reserva'),

    path('manual/', views.manual_usuario, name='manual_usuario'),
    path('manual/descargar/', views.descargar_manual_pdf, name='descargar_manual_pdf'),

    path('reporte/pdf/', views.descargar_reporte_pdf, name='descargar_reporte_pdf'),
]
