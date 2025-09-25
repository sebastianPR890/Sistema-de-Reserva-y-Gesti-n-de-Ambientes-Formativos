from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Ambiente
from .forms import AmbienteForm, BusquedaAmbienteForm

def lista_ambientes(request):
    """
    Vista para listar, buscar y filtrar ambientes.
    """
    form_busqueda = BusquedaAmbienteForm(request.GET)
    ambientes = Ambiente.objects.all()

    # Aplica los filtros de búsqueda si el formulario es válido
    if form_busqueda.is_valid():
        busqueda = form_busqueda.cleaned_data.get('busqueda')
        tipo = form_busqueda.cleaned_data.get('tipo')
        capacidad_min = form_busqueda.cleaned_data.get('capacidad_min')
        solo_activos = form_busqueda.cleaned_data.get('solo_activos')
        con_computadores = form_busqueda.cleaned_data.get('con_computadores')
        con_escritorios = form_busqueda.cleaned_data.get('con_escritorios')
        con_tablero_digital = form_busqueda.cleaned_data.get('con_tablero_digital')

        if busqueda:
            ambientes = ambientes.filter(
                Q(codigo__icontains=busqueda) |
                Q(nombre__icontains=busqueda) |
                Q(ubicacion__icontains=busqueda)
            )

        if tipo:
            ambientes = ambientes.filter(tipo=tipo)

        if capacidad_min:
            ambientes = ambientes.filter(capacidad__gte=capacidad_min)

        if solo_activos:
            ambientes = ambientes.filter(activo=True)

        if con_computadores:
            # Los lookups en JSONField buscan por clave y valor
            ambientes = ambientes.filter(recursos__computadores=True)

        if con_escritorios:
            ambientes = ambientes.filter(recursos__escritorios=True)

        if con_tablero_digital:
            ambientes = ambientes.filter(recursos__tablero_digital=True)

    # Ordena los resultados para consistencia
    ambientes = ambientes.order_by('codigo')

    # Configura la paginación para 10 ambientes por página
    paginator = Paginator(ambientes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'ambientes': page_obj,
        'form_busqueda': form_busqueda,
    }
    return render(request, 'ambientes/lista_ambientes.html', context)

class AmbienteCreateView( CreateView):
    """
    Vista genérica para crear un nuevo ambiente.
    """
    model = Ambiente
    form_class = AmbienteForm
    template_name = 'ambientes/ambiente_form.html'
    success_url = reverse_lazy('ambientes:lista_ambientes')

    def form_valid(self, form):
        messages.success(self.request, "Ambiente creado exitosamente.")
        return super().form_valid(form)

class AmbienteUpdateView( UpdateView):
    """
    Vista genérica para editar un ambiente existente.
    """
    model = Ambiente
    form_class = AmbienteForm
    template_name = 'ambientes/ambiente_form.html'
    success_url = reverse_lazy('ambientes:lista_ambientes')

    def form_valid(self, form):
        messages.success(self.request, "Ambiente actualizado exitosamente.")
        return super().form_valid(form)

class AmbienteDetailView( DetailView):
    """
    Vista genérica para mostrar los detalles de un ambiente.
    """
    model = Ambiente
    template_name = 'ambientes/ambiente_detalle.html'
    context_object_name = 'ambiente'

class AmbienteDeleteView( DeleteView):
    """
    Vista genérica para eliminar un ambiente.
    """
    model = Ambiente
    template_name = 'ambientes/ambiente_confirm_delete.html'
    success_url = reverse_lazy('ambientes:lista_ambientes')

    def form_valid(self, form):
        messages.success(self.request, "Ambiente eliminado exitosamente.")
        return super().form_valid(form)
    
def verificar_disponibilidad(request):
    """
    Vista AJAX para verificar la disponibilidad de un ambiente.
    """
    # Se recomienda verificar si la solicitud es una llamada AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        ambiente_id = request.GET.get('ambiente_id')
        fecha_inicio_str = request.GET.get('fecha_inicio')
        fecha_fin_str = request.GET.get('fecha_fin')
        # Parámetro opcional para excluir una reserva específica (por ejemplo, al editar)
        exclude_reserva_id = request.GET.get('exclude_reserva_id', None)

        if not all([ambiente_id, fecha_inicio_str, fecha_fin_str]):
            return JsonResponse({'disponible': False, 'mensaje': 'Faltan datos de la reserva.'}, status=400)

        try:
            ambiente = Ambiente.objects.get(pk=ambiente_id)
            # Convierte las cadenas de fecha a objetos datetime
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_fin = datetime.fromisoformat(fecha_fin_str)
            
            disponible = ambiente.esta_disponible(fecha_inicio, fecha_fin, exclude_reserva_id)
            
            if disponible:
                mensaje = "El ambiente está disponible en las fechas seleccionadas."
            else:
                mensaje = "El ambiente no está disponible. Ya existe una reserva en ese período."
            
            return JsonResponse({'disponible': disponible, 'mensaje': mensaje})

        except Ambiente.DoesNotExist:
            return JsonResponse({'disponible': False, 'mensaje': 'El ambiente no existe.'}, status=404)
        except ValueError:
            return JsonResponse({'disponible': False, 'mensaje': 'Formato de fecha inválido.'}, status=400)

    # Si la solicitud no es AJAX, devuelve un error 403
    return JsonResponse({'disponible': False, 'mensaje': 'Acceso no autorizado.'}, status=403)