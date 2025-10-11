import os
import datetime
import shutil
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.http import FileResponse, Http404

# --- Rutas de Carpetas ---
BACKUP_DIR = settings.BASE_DIR / 'backups_storage'
TRASH_DIR = settings.BASE_DIR / 'backups_storage_trash'

def is_superuser_or_staff(user):
    return user.is_superuser or user.is_staff

# Función auxiliar para obtener la lista de archivos de una carpeta
def get_backup_files_from_dir(directory):
    files_list = []
    # No es necesario crear la carpeta aquí, se hará en backup_status
    
    if os.path.exists(directory):
        files = sorted(os.listdir(directory), key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
        for f in files:
            file_path = os.path.join(directory, f)
            if os.path.isfile(file_path) and f.endswith('.zip'):
                files_list.append({
                    'name': f,
                    'size': round(os.path.getsize(file_path) / (1024 * 1024), 2), # MB
                    'date': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
    return files_list


@user_passes_test(is_superuser_or_staff)
def run_backup(request):
    # ... (código sin cambios) ...
    if request.method == 'POST':
        try:
            call_command('backup_data')
            messages.success(request, "Copia de seguridad ejecutada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al ejecutar la copia de seguridad: {e}")
        return redirect('backups:backup_status')

    return render(request, 'backups/run_backup.html')

@user_passes_test(is_superuser_or_staff)
def backup_status(request):
    # AÑADIR ESTO: Asegurarse de que ambas carpetas existen antes de intentar acceder a ellas
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(TRASH_DIR, exist_ok=True)
    
    # Obtener Backups Activos
    backup_files = get_backup_files_from_dir(BACKUP_DIR)
    
    # Obtener Backups Eliminados (Papelera)
    deleted_files = get_backup_files_from_dir(TRASH_DIR)
    
    return render(request, 'backups/backup_status.html', {
        'backup_files': backup_files,
        'deleted_files': deleted_files
    })


@user_passes_test(is_superuser_or_staff)
def download_backup(request, filename):
    # ... (código sin cambios) ...
    file_path = os.path.join(BACKUP_DIR, filename)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
            return response
        except Exception as e:
            messages.error(request, f"No se pudo descargar el archivo: {e}")
            return redirect('backups:backup_status')
    else:
        messages.error(request, "El archivo de backup solicitado no existe.")
        raise Http404("El archivo de backup solicitado no existe.")


@user_passes_test(is_superuser_or_staff)
def delete_backup(request, filename):
    if request.method == 'POST':
        source_path = os.path.join(BACKUP_DIR, filename)
        destination_path = os.path.join(TRASH_DIR, filename) 

        # Asegúrate de que la papelera exista antes de intentar mover a ella
        os.makedirs(TRASH_DIR, exist_ok=True)

        if os.path.exists(source_path) and os.path.isfile(source_path):
            try:
                # Mover el archivo
                shutil.move(source_path, destination_path)
                messages.success(request, f"El backup '{filename}' ha sido enviado a la papelera.")
            except Exception as e:
                # Este error es el que probablemente ves si la carpeta TRASH no existe o hay un problema de permisos.
                messages.error(request, f"Error al mover el backup '{filename}' a la papelera: {e}")
        else:
            messages.error(request, f"El archivo de backup '{filename}' no existe en la carpeta principal.")
        
    return redirect('backups:backup_status')


@user_passes_test(is_superuser_or_staff)
def restore_backup(request, filename):
    if request.method == 'POST':
        source_path = os.path.join(TRASH_DIR, filename) 
        destination_path = os.path.join(BACKUP_DIR, filename) 
        
        # Asegúrate de que la carpeta principal exista antes de mover a ella
        os.makedirs(BACKUP_DIR, exist_ok=True)

        if os.path.exists(source_path) and os.path.isfile(source_path):
            try:
                # Mover el archivo de vuelta a la carpeta principal
                shutil.move(source_path, destination_path)
                messages.success(request, f"✅ ¡El backup **{filename}** se ha reestablecido y ha vuelto a la lista principal!")
            except Exception as e:
                messages.error(request, f"Error al reestablecer el backup **{filename}**: {e}")
        else:
            messages.error(request, f"El archivo de backup '{filename}' no se encuentra en la papelera.")
    
    return redirect('backups:backup_status')