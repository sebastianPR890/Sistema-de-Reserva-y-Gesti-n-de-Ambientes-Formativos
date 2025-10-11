# backups/management/commands/backup_data.py
import os
import shutil
import datetime
from zipfile import ZipFile, ZIP_DEFLATED

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Necesario para obtener el nombre del archivo SQLite

# Si vas a usar AWS S3, necesitarás boto3 y configurar tus credenciales en settings.py
# import boto3 
# from botocore.exceptions import NoCredentialsError

class Command(BaseCommand):
    help = 'Crea una copia de seguridad de la base de datos (SQLite) y los archivos de medios.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando proceso de copia de seguridad...'))

        # Obtener la ruta de la base de datos (específico para SQLite)
        db_engine = settings.DATABASES['default']['ENGINE']
        db_path = None
        if 'sqlite3' in db_engine:
            db_path = settings.DATABASES['default']['NAME']
            self.stdout.write(f'Detectada base de datos SQLite en: {db_path}')
        else:
            self.stdout.write(self.style.WARNING('Advertencia: Este comando está optimizado para SQLite.'))
            self.stdout.write(self.style.WARNING('Para otras DBs (MySQL/PostgreSQL), se recomienda usar las herramientas nativas (ej. pg_dump/mysqldump) o servicios como AWS RDS backups.'))
            # Si no es SQLite y no vamos a subir a S3, podríamos detener el proceso de DB aquí
            # raise CommandError('La base de datos no es SQLite. Por favor, usa pg_dump o mysqldump.')


        media_root = settings.MEDIA_ROOT
        
        # Carpeta temporal para almacenar los archivos antes de comprimirlos
        # Asegúrate de que esta carpeta no se suba a Git (añadir a .gitignore)
        backup_temp_dir = settings.BASE_DIR / 'temp_backup_data'
        os.makedirs(backup_temp_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'full_backup_{timestamp}.zip'
        full_backup_path_compressed = settings.BASE_DIR / 'backups_storage' / backup_filename # Guardar el zip final en una carpeta específica
        
        # Asegurarse de que la carpeta de almacenamiento final exista
        os.makedirs(os.path.dirname(full_backup_path_compressed), exist_ok=True)


        try:
            # 1. Copiar base de datos (solo si es SQLite)
            if db_path and os.path.exists(db_path):
                shutil.copy(db_path, backup_temp_dir / os.path.basename(db_path)) # Copiar con el nombre original
                self.stdout.write(self.style.SUCCESS(f'Base de datos SQLite copiada a {backup_temp_dir}'))
            elif db_path: # Si db_path existe pero el archivo no
                self.stdout.write(self.style.WARNING(f'Advertencia: Archivo de base de datos no encontrado en {db_path}. ¿Es la ruta correcta?'))
            
            # 2. Copiar archivos de medios
            if os.path.exists(media_root) and os.listdir(media_root): # Comprobar que la carpeta existe y no está vacía
                # shutil.copytree copiará la carpeta 'media_root' completa dentro de 'temp_backup_data'
                shutil.copytree(media_root, backup_temp_dir / 'media', dirs_exist_ok=True)
                self.stdout.write(self.style.SUCCESS(f'Archivos de medios copiados a {backup_temp_dir}/media'))
            elif not os.path.exists(media_root):
                self.stdout.write(self.style.WARNING(f'Advertencia: La carpeta MEDIA_ROOT no existe en {media_root}. Asegúrate de que settings.MEDIA_ROOT está configurado correctamente.'))
            else:
                self.stdout.write(self.style.WARNING(f'Advertencia: La carpeta MEDIA_ROOT ({media_root}) está vacía. No se copiaron archivos de medios.'))


            # 3. Comprimir los archivos de la carpeta temporal
            with ZipFile(full_backup_path_compressed, 'w', ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(backup_temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calcula la ruta relativa dentro del zip (ej. 'db.sqlite3' o 'media/foto.jpg')
                        arcname = os.path.relpath(file_path, backup_temp_dir)
                        zipf.write(file_path, arcname)
            
            self.stdout.write(self.style.SUCCESS(f'Backup comprimido creado en: {full_backup_path_compressed}'))

            # 4. Opcional: Subir a AWS S3 (descomentar y configurar si usas S3)
            # Asegúrate de tener las siguientes configuraciones en settings.py:
            # AWS_ACCESS_KEY_ID = 'TU_KEY'
            # AWS_SECRET_ACCESS_KEY = 'TU_SECRET_KEY'
            # AWS_STORAGE_BUCKET_NAME = 'tu-bucket-de-s3'
            # AWS_S3_REGION_NAME = 'tu-region-aws'

            # if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID and \
            #    hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') and settings.AWS_STORAGE_BUCKET_NAME:
            #     self.stdout.write(self.style.SUCCESS('Intentando subir backup a AWS S3...'))
            #     try:
            #         s3_client = boto3.client('s3', 
            #                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            #                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            #                                  region_name=getattr(settings, 'AWS_S3_REGION_NAME', None))
            #         
            #         s3_client.upload_file(str(full_backup_path_compressed), 
            #                                 settings.AWS_STORAGE_BUCKET_NAME, 
            #                                 f'backups/{backup_filename}')
            #         self.stdout.write(self.style.SUCCESS(f'Backup {backup_filename} subido a S3 bucket {settings.AWS_STORAGE_BUCKET_NAME}'))
            #     except NoCredentialsError:
            #         self.stdout.write(self.style.ERROR("Error de credenciales de AWS. No se pudo subir el backup a S3."))
            #     except Exception as e:
            #         self.stdout.write(self.style.ERROR(f"Error al subir el backup a S3: {e}"))
            # else:
            #     self.stdout.write(self.style.WARNING('Configuración de AWS S3 incompleta en settings.py. Omitiendo subida a S3.'))

        except Exception as e:
            raise CommandError(f'Ocurrió un error durante la copia de seguridad: {e}')
        finally:
            # Limpiar la carpeta temporal
            if os.path.exists(backup_temp_dir):
                shutil.rmtree(backup_temp_dir)
                self.stdout.write(self.style.SUCCESS(f'Carpeta temporal {backup_temp_dir} eliminada.'))

        self.stdout.write(self.style.SUCCESS('Copia de seguridad completada exitosamente.'))