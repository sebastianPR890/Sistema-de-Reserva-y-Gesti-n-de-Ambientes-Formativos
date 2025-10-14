import os
import datetime
import shutil
from zipfile import ZipFile
import psycopg2
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.http import FileResponse, Http404
import subprocess

# --- Rutas de Carpetas ---
BACKUP_DIR = settings.BASE_DIR / 'backups_storage'
TRASH_DIR = settings.BASE_DIR / 'backups_storage_trash'

def is_superuser_or_staff(user):
    return user.is_superuser or user.is_staff

# Función auxiliar para obtener la lista de archivos de una carpeta
def get_backup_files_from_dir(directory, search_name=None, search_date=None):
    files_list = []
    
    if os.path.exists(directory):
        # 1. Obtener todos los archivos .zip y ordenarlos por fecha de modificación
        files = sorted(os.listdir(directory), key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
        
        for f in files:
            file_path = os.path.join(directory, f)
            
            if os.path.isfile(file_path) and f.endswith('.zip'):
                
                # 2. Obtener metadatos del archivo
                file_date_timestamp = os.path.getmtime(file_path)
                file_datetime_obj = datetime.datetime.fromtimestamp(file_date_timestamp)
                file_date_str = file_datetime_obj.strftime('%Y-%m-%d')
                
                # --- Aplicar Filtros ---
                match_name = True
                match_date = True
                
                # Filtro por Nombre
                if search_name and search_name.strip():
                    if search_name.lower() not in f.lower():
                        match_name = False
                        
                # Filtro por Fecha de Creación
                if search_date and search_date.strip():
                    # Compara solo la parte de la fecha (AAAA-MM-DD)
                    if search_date != file_date_str:
                        match_date = False
                
                # 3. Si el archivo coincide con todos los filtros, agregarlo a la lista
                if match_name and match_date:
                    files_list.append({
                        'name': f,
                        'size': round(os.path.getsize(file_path) / (1024 * 1024), 2), # MB
                        'date': file_datetime_obj.strftime('%Y-%m-%d %H:%M:%S'),
                        'date_short': file_date_str # Útil para pre-llenar el campo de fecha
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

# ... (código anterior) ...

@user_passes_test(is_superuser_or_staff)
def backup_status(request):
    # AÑADIR ESTO: Asegurarse de que ambas carpetas existen antes de intentar acceder a ellas
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(TRASH_DIR, exist_ok=True)

    # Obtener parámetros de búsqueda de la URL
    search_name = request.GET.get('nombre', '').strip()
    search_date = request.GET.get('fecha', '').strip()
    
    # Obtener Backups Activos, aplicando filtros
    backup_files = get_backup_files_from_dir(
        BACKUP_DIR, 
        search_name=search_name, 
        search_date=search_date
    )
    
    # Obtener Backups Eliminados (Papelera), aplicando filtros
    deleted_files = get_backup_files_from_dir(
        TRASH_DIR, 
        search_name=search_name, 
        search_date=search_date
    )
    
    # Crear un diccionario para mantener los valores de filtro y rellenar el formulario
    filter_data = {
        'nombre': search_name,
        'fecha': search_date,
    }

    return render(request, 'backups/backup_status.html', {
        'backup_files': backup_files,
        'deleted_files': deleted_files,
        'filter_data': filter_data, # Pasar los datos del filtro al template
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


@user_passes_test(is_superuser_or_staff)
def restore_backup_file(request, filename):
    if request.method == 'POST':
        try:
            # Rutas de archivos
            backup_path = os.path.join(BACKUP_DIR, filename)
            temp_dir = os.path.join(settings.BASE_DIR, 'temp_restore')

            if not os.path.exists(backup_path):
                messages.error(request, "El archivo de backup no existe.")
                return redirect('backups:backup_status')

            # Crear directorio temporal
            os.makedirs(temp_dir, exist_ok=True)

            # Extraer el backup
            with ZipFile(backup_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Buscar archivo SQL
            sql_backup = None
            for file in os.listdir(temp_dir):
                if file.endswith('.sql'):
                    sql_backup = os.path.join(temp_dir, file)
                    break

            if sql_backup:
                try:
                    db_settings = settings.DATABASES['default']
                    env = os.environ.copy()
                    env['PGPASSWORD'] = db_settings['PASSWORD']

                    # Comando psql para restaurar
                    restore_command = [
                        'psql',
                        f"-h{db_settings['HOST']}",
                        f"-p{db_settings['PORT']}",
                        f"-U{db_settings['USER']}",
                        f"-d{db_settings['NAME']}",
                        '-v', 'ON_ERROR_STOP=1',
                        '--single-transaction',
                        '-f', sql_backup
                    ]

                    result = subprocess.run(
                        restore_command,
                        env=env,
                        capture_output=True,
                        text=True
                    )

                    if result.returncode != 0:
                        raise Exception(f"Error en la restauración: {result.stderr}")

                    messages.success(request, "Base de datos restaurada exitosamente.")

                except Exception as e:
                    raise Exception(f"Error al restaurar la base de datos: {str(e)}")

            # Restaurar archivos media
            media_backup = os.path.join(temp_dir, 'media')
            if os.path.exists(media_backup):
                media_path = settings.MEDIA_ROOT
                if os.path.exists(media_path):
                    shutil.rmtree(media_path)
                shutil.copytree(media_backup, media_path)

            messages.success(request, f"El backup {filename} ha sido restaurado exitosamente.")

        except Exception as e:
            messages.error(request, f"Error al restaurar el backup: {str(e)}")

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    return redirect('backups:backup_status')