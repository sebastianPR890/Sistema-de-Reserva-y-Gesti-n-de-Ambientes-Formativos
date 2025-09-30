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

@login_required
def lista_equipos(request):
    """
    Redireccionar a la lista de ambientes en lugar de mostrar lista de equipos
    """
    return redirect('ambientes:lista')

class EquipoCreateView(LoginRequiredMixin, CreateView):
    """
    Vista genérica para crear un nuevo equipo.
    """
    model = Equipo
    form_class = EquipoForm
    template_name = 'equipos/equipo_form.html'
    success_url = reverse_lazy('equipos:lista_equipos')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "No tienes permisos para crear equipos.")
            return redirect('ambientes:lista')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, "Equipo creado exitosamente.")
        return super().form_valid(form)

class EquipoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista genérica para editar un equipo existente.
    """
    model = Equipo
    form_class = EquipoForm
    template_name = 'equipos/equipo_form.html'
    success_url = reverse_lazy('equipos:lista_equipos')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "No tienes permisos para editar equipos.")
            return redirect('ambientes:lista')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ambiente'] = self.object.ambiente
        return context

    def form_valid(self, form):
        messages.success(self.request, "Equipo actualizado exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ambientes:detalle', kwargs={'pk': self.object.ambiente.pk})

class EquipoDetailView( DetailView):
    """
    Vista genérica para mostrar los detalles de un equipo.
    """
    model = Equipo
    template_name = 'equipos/equipo_detalle.html'
    context_object_name = 'equipo'

class EquipoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista genérica para eliminar un equipo.
    """
    model = Equipo
    template_name = 'equipos/equipo_confirm_delete.html'
    success_url = reverse_lazy('equipos:lista_equipos')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "No tienes permisos para eliminar equipos.")
            return redirect('ambientes:lista')
        return super().dispatch(request, *args, **kwargs)
    
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