from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import (
    CreateView, UpdateView, DetailView, DeleteView, ListView
)
from django.urls import reverse_lazy, reverse

from .models import Equipo, MovimientoEquipo
from .forms import EquipoForm, BusquedaEquipoForm, MovimientoEquipoForm

def lista_equipos(request):
    """
    Vista para listar, buscar y filtrar equipos.
    """
    form_busqueda = BusquedaEquipoForm(request.GET)
    equipos = Equipo.objects.all()

    if form_busqueda.is_valid():
        busqueda = form_busqueda.cleaned_data.get('busqueda')
        estado = form_busqueda.cleaned_data.get('estado')
        activo = form_busqueda.cleaned_data.get('activo')
        
        if busqueda:
            equipos = equipos.filter(
                Q(codigo__icontains=busqueda) |
                Q(nombre__icontains=busqueda) |
                Q(serie__icontains=busqueda)
            )

        if estado:
            equipos = equipos.filter(estado=estado)

        if activo:
            equipos = equipos.filter(activo=True)

    equipos = equipos.order_by('codigo')

    paginator = Paginator(equipos, 10)  # 10 equipos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'equipos': page_obj,
        'form_busqueda': form_busqueda,
    }
    return render(request, 'equipos/lista_equipos.html', context)

class EquipoCreateView( CreateView):
    """
    Vista genérica para crear un nuevo equipo.
    """
    model = Equipo
    form_class = EquipoForm
    template_name = 'equipos/equipo_form.html'
    success_url = reverse_lazy('equipos:lista_equipos')
    
    def form_valid(self, form):
        messages.success(self.request, "Equipo creado exitosamente.")
        return super().form_valid(form)

class EquipoUpdateView( UpdateView):
    """
    Vista genérica para editar un equipo existente.
    """
    model = Equipo
    form_class = EquipoForm
    template_name = 'equipos/equipo_form.html'
    success_url = reverse_lazy('equipos:lista_equipos')

    def form_valid(self, form):
        messages.success(self.request, "Equipo actualizado exitosamente.")
        return super().form_valid(form)

class EquipoDetailView( DetailView):
    """
    Vista genérica para mostrar los detalles de un equipo.
    """
    model = Equipo
    template_name = 'equipos/equipo_detalle.html'
    context_object_name = 'equipo'

class EquipoDeleteView( DeleteView):
    """
    Vista genérica para eliminar un equipo.
    """
    model = Equipo
    template_name = 'equipos/equipo_confirm_delete.html'
    success_url = reverse_lazy('equipos:lista_equipos')
    
    def form_valid(self, form):
        messages.success(self.request, "Equipo eliminado exitosamente.")
        return super().form_valid(form)

class MovimientoEquipoCreateView( CreateView):
    """
    Vista para crear un nuevo movimiento de equipo.
    """
    model = MovimientoEquipo
    form_class = MovimientoEquipoForm
    template_name = 'equipos/movimiento_form.html'
    
    def get_success_url(self):
        # Redirige a la página de detalles del equipo después de un movimiento
        return reverse('equipos:equipo_detalle', kwargs={'pk': self.object.equipo.pk})
        
    def form_valid(self, form):
        messages.success(self.request, "Movimiento de equipo registrado exitosamente.")
        return super().form_valid(form)

class MovimientoEquipoListView( ListView):
    """
    Vista para listar todos los movimientos de equipos.
    """
    model = MovimientoEquipo
    template_name = 'equipos/lista_movimientos.html'
    context_object_name = 'movimientos'
    paginate_by = 10
    ordering = ['-fecha_movimiento']