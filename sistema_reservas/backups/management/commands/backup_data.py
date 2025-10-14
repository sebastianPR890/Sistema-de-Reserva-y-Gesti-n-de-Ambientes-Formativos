# backups/management/commands/backup_data.py
import os
import shutil
import datetime
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED
import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Crea una copia de seguridad de la base de datos PostgreSQL y los archivos de medios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando proceso de copia de seguridad...'))

        # Configuración de la base de datos
        db_settings = settings.DATABASES['default']
        
        # Crear carpetas necesarias
        backup_temp_dir = str(settings.BASE_DIR / 'temp_backup_data')
        os.makedirs(backup_temp_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        sql_filename = f'backup_{timestamp}.sql'
        sql_path = os.path.join(backup_temp_dir, sql_filename)
        
        try:
            # Configurar variables de entorno para autenticación
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['PASSWORD']

            # Comando pg_dump para backup
            dump_command = [
                'pg_dump',
                f"-h{db_settings['HOST']}",
                f"-p{db_settings['PORT']}",
                f"-U{db_settings['USER']}",
                f"-d{db_settings['NAME']}",
                '--clean',  # Agregar DROP antes de CREATE
                '--if-exists',  # Evitar errores si los objetos no existen
                '--no-owner',  # No incluir comandos para establecer el propietario
                '--no-privileges',  # No incluir comandos para establecer privilegios
                '-Fp',  # Formato plain
                '-f', sql_path
            ]

            # Ejecutar pg_dump
            result = subprocess.run(
                dump_command,
                env=env,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise CommandError(f"Error en pg_dump: {result.stderr}")

            self.stdout.write(self.style.SUCCESS('Base de datos respaldada exitosamente'))

            # Copiar archivos media
            media_root = str(settings.MEDIA_ROOT)
            media_backup_path = os.path.join(backup_temp_dir, 'media')
            
            if os.path.exists(media_root):
                if os.path.exists(media_backup_path):
                    shutil.rmtree(media_backup_path)
                shutil.copytree(media_root, media_backup_path)
                self.stdout.write(self.style.SUCCESS('Archivos media copiados exitosamente'))

            # Crear ZIP final
            backup_filename = f'full_backup_{timestamp}.zip'
            backup_dir = str(settings.BASE_DIR / 'backups_storage')
            os.makedirs(backup_dir, exist_ok=True)
            full_backup_path = os.path.join(backup_dir, backup_filename)

            with ZipFile(full_backup_path, 'w', ZIP_DEFLATED) as zipf:
                # Verificar y agregar SQL dump
                if os.path.exists(sql_path) and os.path.getsize(sql_path) > 0:
                    zipf.write(sql_path, os.path.basename(sql_path))
                    self.stdout.write(self.style.SUCCESS(f'SQL dump agregado al ZIP ({os.path.getsize(sql_path)} bytes)'))
                else:
                    raise CommandError("El archivo SQL dump está vacío o no se creó correctamente")

                # Agregar archivos media
                if os.path.exists(media_backup_path):
                    for root, _, files in os.walk(media_backup_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('media', os.path.relpath(file_path, media_backup_path))
                            zipf.write(file_path, arcname)

            self.stdout.write(self.style.SUCCESS(f'Backup creado exitosamente en: {full_backup_path}'))

        except Exception as e:
            raise CommandError(f'Error durante el backup: {str(e)}')

        finally:
            if os.path.exists(backup_temp_dir):
                shutil.rmtree(backup_temp_dir)