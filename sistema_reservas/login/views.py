from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.models import Usuario
from .forms import CustomLoginForm, CustomRegistroForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        documento = request.POST.get('username')  # El campo se llama username en el form
        password = request.POST.get('password')
        
        try:
            # Primero buscamos por documento
            user = Usuario.objects.get(documento=documento)
            # Intentamos autenticar usando el username (que es igual al documento)
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.nombre_completo()}')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('/')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese documento')
    
    form = CustomLoginForm()
    return render(request, 'login/login.html', {'form': form})

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        form = CustomRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro exitoso')
            return redirect('/')
    else:
        form = CustomRegistroForm()
    
    return render(request, 'login/registro.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login:login')
