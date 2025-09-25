from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/reservas/', permanent=False)),
    path('usuarios/', include('usuarios.urls')),
    path('ambientes/', include('ambientes.urls')),
    path('reservas/', include('reservas.urls')),
    path('equipos/', include('equipos.urls')),
    path('notificaciones/', include('notificaciones.urls')),
]
