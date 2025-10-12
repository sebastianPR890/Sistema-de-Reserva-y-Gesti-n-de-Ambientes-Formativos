from django.urls import path
from . import views

app_name = 'backups'

urlpatterns = [
    path('run/', views.run_backup, name='run_backup'),
    path('status/', views.backup_status, name='backup_status'),
    path('download/<str:filename>/', views.download_backup, name='download_backup'),
    path('delete/<str:filename>/', views.delete_backup, name='delete_backup'),
    # Asegúrate de que esta ruta esté correcta
    path('restore/<str:filename>/', views.restore_backup, name='restore_backup'), 
]