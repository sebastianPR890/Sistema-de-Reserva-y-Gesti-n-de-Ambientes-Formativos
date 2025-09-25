from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('ambientes/', include('ambientes.urls')),
    path('equipos/', include('equipos.urls')),
    path('notificaciones/', include('notificaciones.urls')),
]
