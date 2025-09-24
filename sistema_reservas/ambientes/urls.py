# ambientes/urls.py
from django.urls import path
from . import views

app_name = 'ambientes'

urlpatterns = [
    # URLs principales
    path('', views.lista_ambientes, name='lista'),
    path('crear/', views.AmbienteCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.AmbienteDetailView, name='detalle'),
    path('<int:pk>/editar/', views.AmbienteUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.AmbienteDeleteView, name='eliminar'),
    
    # URLs AJAX y API
    path('verificar_disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
]