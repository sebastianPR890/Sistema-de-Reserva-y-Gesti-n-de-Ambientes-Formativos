from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.models import Usuario  
from .forms import CustomLoginForm, CustomRegistroForm

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.urls import reverse


# --- Vistas de Manual de Usuario ---

def manual_usuario_view(request):
    return render(request, 'manual/manual_usuario.html')


# --- Vistas de Autenticación ---

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


# --- Vistas de Recuperación de Contraseña ---

def recu_contra(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            # 1. Buscar al usuario
            user = Usuario.objects.get(email=email) 
            
            # --- CORRECCIÓN CLAVE INICIA AQUÍ ---
            
            # 2. Guarda el email del usuario
            recovery_email = user.email

            # 3. Se crea una instancia de TimestampSigner
            signer = TimestampSigner()
            
            # 4. Se firma el id del usuario para generar un token único
            token = signer.sign(str(user.pk))  # <-- 'token' se define aquí
            
            # 5. Se construye la URL absoluta USANDO el token
            reset_url = request.build_absolute_uri(reverse('login:cambia_con', args=[token]))
            
            # 6. Se renderiza la plantilla del mensaje de correo
            html_message = render_to_string('login/msg_correo.html', {
                'username': user.documento,
                'reset_url': reset_url,
                'site_name': 'Sistema de Reservas SENA',
            })
            
            subject = "Recuperación de contraseña"
            text_message = strip_tags(html_message)
            
            # --- CORRECCIÓN CLAVE TERMINA AQUÍ ---
            
        except Usuario.DoesNotExist:
            messages.error(request, "El correo ingresado no está registrado.")
            return render(request, 'login/recuperar_contraseña.html')
        
        
        try:
            # Se prepara el correo (resto del código de envío)
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recovery_email]
            )
            
            # Adjuntamos la versión HTML (la corrección que hicimos antes)
            email.attach_alternative(html_message, "text/html") 
            
            email.encoding = 'utf-8'
            email.send()
            
            messages.success(request, "Se ha enviado un enlace a tu correo de recuperación para cambiar la contraseña.")
            return redirect("login:login") 
        except Exception as e:
            messages.error(request, f"Error al enviar el correo: {str(e)}")
            return render(request, 'login/recuperar_contraseña.html')
        
    return render(request, 'login/recuperar_contraseña.html')

def cambia_con(request, token):
    signer = TimestampSigner()
    try:
        user_id = signer.unsign(token, max_age=3600)
        # CORRECCIÓN: Usamos el modelo Usuario
        usuario = get_object_or_404(Usuario, pk=user_id) 
    except (BadSignature, SignatureExpired):
        messages.error(request, "El enlace de recuperación es inválido o ha expirado.")
        # CORRECCIÓN: Redirige a la recuperación con el namespace correcto
        return redirect("login:recu_contra")
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'login/cambia_contraseña.html')
        
        usuario.password = make_password(new_password)
        usuario.save()
        
        messages.success(request, "La contraseña se ha cambiado correctamente.")
        # CORRECCIÓN: Redirige al login con el namespace correcto
        return redirect("login:login") 
    
    return render(request, 'login/cambia_contraseña.html')