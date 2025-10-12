from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Ambiente
from .forms import AmbienteForm, BusquedaAmbienteForm, CrearAmbienteForm
from equipos.forms import EquipoForm
from equipos.models import Equipo

def lista_ambientes(request):
    """
    Vista para listar, buscar y filtrar ambientes.
    """
    form_busqueda = BusquedaAmbienteForm(request.GET)
    ambientes = Ambiente.objects.all()

    # Aplica los filtros de búsqueda si el formulario es válido
    if form_busqueda.is_valid():
        cleaned_data = form_busqueda.cleaned_data
        
        # 1. Filtro de Búsqueda por Texto (código o nombre)
        busqueda = cleaned_data.get('busqueda')
        if busqueda:
            ambientes = ambientes.filter(
                Q(codigo__icontains=busqueda) | Q(nombre__icontains=busqueda)
            )
            
        # 2. Filtro por Tipo de Ambiente
        tipo = cleaned_data.get('tipo')
        if tipo:
            ambientes = ambientes.filter(tipo=tipo)
            
        # 3. Filtro por Capacidad Mínima
        capacidad_min = cleaned_data.get('capacidad_min')
        if capacidad_min:
            ambientes = ambientes.filter(capacidad__gte=capacidad_min)

        # 4. FILTRO BOOLEANO: Solo Ambientes Activos (activo=True)
        solo_activos = cleaned_data.get('solo_activos')
        if solo_activos:
            # Si la casilla está marcada, solo muestra los activos (True)
            ambientes = ambientes.filter(activo=True)
        # Nota: Si no está marcada, no se filtra por activo, mostrando ambos.
            
        # 5. FILTRO BOOLEANO: Con Computadores 
        con_computadores = cleaned_data.get('con_computadores')
        if con_computadores:
            # Buscamos en la relación 'equipos' (el related_name/default) que su nombre contenga 'Computador'
            ambientes = ambientes.filter(
                equipos__nombre__icontains='Computador' 
            ).distinct() # Usamos distinct para evitar duplicados si un ambiente tiene varios computadores
            
        # 6. FILTRO BOOLEANO: Con Escritorios
        con_escritorios = cleaned_data.get('con_escritorios')
        if con_escritorios:
            # Buscamos en la relación 'equipos' que su nombre contenga 'Escritorio'
            ambientes = ambientes.filter(
                equipos__nombre__icontains='Escritorio'
            ).distinct()
            
        # 7. FILTRO BOOLEANO: Con Tablero Digital
        con_tablero_digital = cleaned_data.get('con_tablero_digital')
        if con_tablero_digital:
            # Buscamos en la relación 'equipos' que su nombre contenga 'Tablero Digital'
            ambientes = ambientes.filter(
                equipos__nombre__icontains='Tablero Digital' 
            ).distinct()


    # ... (Paginación y renderizado)
    paginator = Paginator(ambientes, 10)  # Muestra 10 ambientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form_busqueda': form_busqueda,
        'page_obj': page_obj,
        'ambientes': ambientes, # Se envía el QuerySet filtrado
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

@login_required
def crear_ambiente(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para crear ambientes')
        return redirect('ambientes:lista')
        
    if request.method == 'POST':
        form = CrearAmbienteForm(request.POST)
        if form.is_valid():
            ambiente = form.save()
            messages.success(request, f'Ambiente {ambiente.nombre} creado exitosamente')
            return redirect('ambientes:lista')
    else:
        form = CrearAmbienteForm()
    
    return render(request, 'ambientes/crear_ambiente.html', {'form': form})

@login_required
def agregar_equipo(request, ambiente_id):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para agregar equipos')
        return redirect('ambientes:detalle', pk=ambiente_id)
        
    ambiente = get_object_or_404(Ambiente, pk=ambiente_id)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.ambiente = ambiente
            equipo.save()
            messages.success(request, f'Equipo {equipo.nombre} agregado exitosamente')
            return redirect('ambientes:detalle', pk=ambiente_id)
    else:
        form = EquipoForm()
    
    return render(request, 'ambientes/agregar_equipo.html', {
        'form': form,
        'ambiente': ambiente
    })